# src/meshtastic/tcp_connection.py

import asyncio
import socket
from typing import Any, Dict

from asyncio import get_running_loop

from connection.connection import Connection
from protobufs.proto_utils import extract_frames


class TcpConnection(Connection):
    def __init__(self):
        super().__init__()
        self.conn_id = None
        self.host = None
        self.port = None
        self.socket = None
        self.buffer = b""
        self.connected = False
        self.connected_promise = None
        self._recv_task: None

    # -------------------------------------------------------------------------
    # Connection meta
    # -------------------------------------------------------------------------

    def _meta(self) -> Dict[str, Any]:
        """
        Base metadata about this connection. This will be further enriched
        by Connection.on_received_packet() with connId, timestamp, and
        meta_overrides.
        """
        return {
            "connId": self.conn_id,
            "host": self.host,
            "port": self.port,
            "transport": "tcp",
        }

    # -------------------------------------------------------------------------
    # Lifecycle
    # -------------------------------------------------------------------------

    async def connect(self, conn_id, host, port):
        self.conn_id = conn_id
        self.host = host
        self.port = port
        self.connected_promise = get_running_loop().create_future()
        self._recv_task: asyncio.Task | None = None

        """
        Establish the TCP connection and start the receive loop.

        Resolves connected_promise on success, or sets an exception on failure.
        """
        if self.connected:
            # Already connected; nothing to do
            return

        print(f"[TcpConnection {self.conn_id}] Connecting to {self.host}:{self.port}...")

        loop = asyncio.get_running_loop()

        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Non-blocking for use with loop.sock_recv
            self.socket.setblocking(False)

            await loop.sock_connect(self.socket, (self.host, self.port))

            self.connected = True
            meta = self._meta()

            if not self.connected_promise.done():
                self.connected_promise.set_result(meta)

            print(f"[TcpConnection {self.conn_id}] Connected to {self.host}:{self.port}")
            print(f"[TcpConnection {self.conn_id}] Startup complete")

            # Start the receive loop
            self._recv_task = asyncio.create_task(self._recv_loop())

        except Exception as err:
            self.connected = False
            if self.socket:
                try:
                    self.socket.close()
                except Exception:
                    pass
                self.socket = None

            if not self.connected_promise.done():
                self.connected_promise.set_exception(err)

            print(f"[TcpConnection {self.conn_id}] Error during connect: {err}")
            raise

    async def _recv_loop(self) -> None:
        """
        Async receive loop:
        - Reads bytes from the TCP socket
        - Uses extract_frames() to split into radio frames
        - For each frame, calls self.on_received_packet(meta, frame)
        """
        if not self.socket:
            print(f"[TcpConnection {self.conn_id}] _recv_loop started with no socket")
            return

        loop = asyncio.get_running_loop()
        print(f"[TcpConnection {self.conn_id}] Receive loop started")

        try:
            while self.connected:
                try:
                    chunk = await loop.sock_recv(self.socket, 4096)
                except (asyncio.CancelledError, SystemExit):
                    print(f"[TcpConnection {self.conn_id}] Receive loop cancelled")
                    break
                except Exception as err:
                    print(f"[TcpConnection {self.conn_id}] Error receiving data: {err}")
                    break

                if not chunk:
                    # Remote closed the connection
                    print(f"[TcpConnection {self.conn_id}] Remote closed connection")
                    break

                # Append to buffer and extract framed messages
                self.buffer += chunk
                result = extract_frames(self.buffer)
                self.buffer = result["remainder"]

                frames = result.get("frames", [])
                if frames:
                    print(
                        f"[TcpConnection {self.conn_id}] "
                        f"Received {len(frames)} frame(s) from stream"
                    )

                for frame in frames:
                    # NOTE: frame is a raw radio frame (bytes)
                    # We feed it into the base Connection, which will:
                    # - decode via decode_from_radio_frame()
                    # - enrich metadata
                    # - emit events / enqueue
                    try:
                        self.on_received_packet(self._meta(), frame)
                    except Exception as err:
                        print(
                            f"[TcpConnection {self.conn_id}] "
                            f"Error processing received frame: {err}"
                        )

        finally:
            # Ensure state is cleaned up
            self.connected = False
            print(f"[TcpConnection {self.conn_id}] Receive loop terminated")
            self._cleanup_socket()

    # -------------------------------------------------------------------------
    # Sending
    # -------------------------------------------------------------------------

    def send_packet(self, buffer: bytes) -> bool:
        """
        Implementation of the abstract Connection.send_packet().

        Sends a raw radio frame over the TCP socket.

        Returns:
            True on success, False if not connected or on error.
        """
        if not self.connected or not self.socket:
            print(
                f"[TcpConnection {self.conn_id}] "
                f"send_packet called with no active connection"
            )
            return False

        try:
            # This is a synchronous send. If you want fully async semantics,
            # you can later refactor this to use loop.sock_sendall in an async
            # method without changing the Connection API right now.
            self.socket.sendall(buffer)
            print(
                f"[TcpConnection {self.conn_id}] "
                f"Sent packet of {len(buffer)} bytes"
            )
            return True
        except Exception as err:
            print(f"[TcpConnection {self.conn_id}] Error sending packet: {err}")
            return False

    # -------------------------------------------------------------------------
    # Shutdown / cleanup
    # -------------------------------------------------------------------------

    def _cleanup_socket(self) -> None:
        """
        Internal helper to close and clear the socket state.
        """
        if self.socket:
            try:
                self.socket.close()
                print(f"[TcpConnection {self.conn_id}] Socket closed")
            except Exception as err:
                print(
                    f"[TcpConnection {self.conn_id}] "
                    f"Error during socket close: {err}"
                )
        self.socket = None
        self.buffer = b""
        self.connected = False

    def close(self) -> None:
        """
        Public close method for this TCP connection.
        Cancels the receive loop (if running) and closes the socket.
        """
        print(f"[TcpConnection {self.conn_id}] Closing connection...")

        self.connected = False

        # Cancel receive loop if running
        if self._recv_task and not self._recv_task.done():
            self._recv_task.cancel()

        self._cleanup_socket()
        print(f"[TcpConnection {self.conn_id}] Connection terminated")

    def shutdown(self) -> None:
        """
        Backwards-compatible shutdown API (mirrors old TcpSocket.shutdown).
        """
        print(f"[TcpConnection {self.conn_id}] Shutting down...")
        self.close()
        print(f"[TcpConnection {self.conn_id}] Shutdown complete")
