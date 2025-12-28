import asyncio
import socket
import time
import traceback
import logging

import meshcore_py
from meshcore_py.packets import Packet
from meshcore_py.buffer.buffer_reader import BufferReader
from meshcore_py.connection.tcp_connection import TCPConnection
from meshcore_py.constants import Constants
from .port_nums import port_nums, get_name
from asyncio import get_running_loop


class MeshcoreConnection(TCPConnection):
    def __init__(self):
        super().__init__()
        self.read_buffer = bytearray()
        self._reconnect_in_progress = False
        self._reconnect_attempts = 0

        # Request API wrapper
        # self.request = MeshcoreRequests(
        #     {"connection": self, "on": handler.on}, timeout_ms=10000
        # )

    def attempt_reconnect(self):
        if self._reconnect_in_progress:
            return
        self._reconnect_in_progress = True

        logging.info(f"[{time.strftime('%Y-%m-%dT%H:%M:%S')}] Attempting reconnect")

        try:
            if self.socket:
                self.socket.close()
        except Exception as err:
            print("Error closing socket during reconnect:", err)
        self.socket = None

        self.emit("connection_lost", {"timestamp": int(time.time() * 1000)})

        self._reconnect_attempts += 1
        delay = min(3000 * self._reconnect_attempts, 15000) / 1000.0  # seconds

        loop = get_running_loop()
        loop.call_later(delay, self._reset_and_connect)

    def _reset_and_connect(self):
        self._reconnect_in_progress = False
        asyncio.create_task(self.connect(self.host, self.port))

    async def connect(self, host: str = None, port: int = None):
        self.host = host or self.host
        self.port = port or self.port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        logging.info(f"[MeshcoreConnection] Connecting to {self.host}:{self.port}")
        try:
            await get_running_loop().sock_connect(self.socket, (self.host, self.port))
            # loop must go before on_connected because part of the connect is receiving
            # a deviceInfo packet.
            asyncio.create_task(self._read_loop())

            # Call the on_connected handler (not await)
            await self.on_connected()   # or self.emit("connected", {...})

            self._reconnect_in_progress = False
        except Exception as e:
            logging.error("[MeshcoreConnection] Connection Error %s", e)
            self.attempt_reconnect()
            return

    async def _read_loop(self):
        try:
            while True:
                data = await get_running_loop().sock_recv(self.socket, 4096)
                if not data:
                    break
                self.on_socket_data_received(data)
        except Exception as e:
            logging.error("[MescoreConnection] Socket read error %s", e)
            self.attempt_reconnect()
        finally:
            if self.socket != None:
                self.socket.close()

    def get_current_ip_address(self):
        return self.socket.getpeername()[0] if self.socket else None

    def on_socket_data_received(self, data: bytes):
        self.read_buffer.extend(data)
        frame_header_length = 3

        while len(self.read_buffer) >= frame_header_length:
            try:
                reader = BufferReader(self.read_buffer[:frame_header_length])
                frame_type = reader.read_byte()
                frame_length = reader.read_uint16_le()
                required_length = frame_header_length + frame_length

                if frame_type not in (
                    Constants.SerialFrameTypes.INCOMING,
                    Constants.SerialFrameTypes.OUTGOING,
                ):
                    self.read_buffer = self.read_buffer[1:]
                    continue

                if not frame_length or len(self.read_buffer) < required_length:
                    break

                frame_data = self.read_buffer[frame_header_length:required_length]
                self.read_buffer = self.read_buffer[required_length:]

                self.route_frame(frame_data)
            except Exception as e:
                print("Failed to process frame", e)
                traceback.print_exc()
                break

    def route_frame(self, frame_data: bytes):
        frame_type = frame_data[0]
        is_structured = frame_type in (
            Constants.SerialFrameTypes.INCOMING,
            Constants.SerialFrameTypes.OUTGOING,
        )

        if not is_structured:
            self.on_frame_received(frame_data)
            return

        if len(frame_data) < 4:
            print(f"Dropping short frame: {len(frame_data)} bytes")
            return

        packet = Packet.from_bytes(frame_data)

        if packet.payload_type != Packet.PAYLOAD_TYPE_RAW_CUSTOM:
            self.on_frame_received(frame_data)
            return

        port_num = self.extract_port_num(packet.payload)
        port_name = get_name(port_num)
        event_name = f"portnum_{port_name}"
        decoded = self.decode_port_payload(port_num, packet.payload)
        self.emit(event_name, decoded)

    def extract_port_num(self, payload: bytes) -> int:
        reader = BufferReader(payload)
        return reader.read_byte()

    def decode_port_payload(self, port_num: int, payload: bytes):
        reader = BufferReader(payload[1:])  # skip portNum
        if port_num == port_nums.Contact:
            return self.decode_contact(reader)
        elif port_num == port_nums.ContactSync:
            return self.decode_contact_sync(reader)
        elif port_num == port_nums.Telemetry:
            return self.decode_telemetry(reader)
        else:
            return {"raw": payload}

    def decode_contact(self, reader: BufferReader):
        contact_id = reader.read_bytes(16).hex()
        alias_len = reader.read_byte()
        alias = reader.read_bytes(alias_len).decode("utf-8")
        last_seen = reader.read_uint32_le()
        rssi = reader.read_int8()
        return {"contactId": contact_id, "alias": alias, "lastSeen": last_seen, "rssi": rssi}

    def decode_contact_sync(self, reader: BufferReader):
        return {"syncData": reader.read_remaining_bytes()}

    def decode_telemetry(self, reader: BufferReader):
        return {"telemetry": reader.read_remaining_bytes()}

    # --- Shutdown ---
    def shutdown(self):
        """Gracefully close socket, stop reconnects, and shutdown request API."""
        print("[MeshcoreConnection] Shutting down...")

        # Cancel reconnect attempts
        self._reconnect_in_progress = False

        # Close socket if open
        if self.socket:
            try:
                self.socket.close()
                print("[MeshcoreConnection] Socket closed.")
            except Exception as e:
                print(f"[MeshcoreConnection] Error closing socket: {e}")
            finally:
                self.socket = None

        # Shutdown request API (cascades into MeshcoreCommandQueue)
        # if self.request:
        #     try:
        #         self.request.shutdown()
        #     except Exception as e:
        #         print(f"[MeshcoreConnection] Error shutting down requests: {e}")
        #     finally:
        #         self.request = None

        print("[MeshcoreConnection] Shutdown complete.")
