# src/meshtastic/tcp_socket.py
import asyncio
import socket
from .packets.frame_parser import extract_frames

class TcpSocket:
    def __init__(self, conn_id, host, port):
        self.conn_id = conn_id
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.buffer = b""
        self.connected = False
        self.connected_promise = asyncio.get_event_loop().create_future()
        self._setup()

    def _setup(self):
        try:
            self.socket.connect((self.host, self.port))
            self.connected = True
            self.connected_promise.set_result(self._meta())
        except Exception as err:
            self.connected = False
            self.connected_promise.set_exception(err)

    def _meta(self):
        return {
            "connId": self.conn_id,
            "host": self.host,
            "port": self.port,
            "transport": "tcp",
        }

    def on_data(self, chunk: bytes):
        self.buffer += chunk
        result = extract_frames(self.buffer)
        self.buffer = result["remainder"]
        for frame in result["frames"]:
            print(f"[TcpSocket {self.conn_id}] Frame received {len(frame)} bytes")

    def write(self, data: bytes):
        if not self.connected:
            print(f"[TcpSocket {self.conn_id}] Write attempted with no active connection")
            return False
        self.socket.sendall(data)
        return True

    def end(self):
        self.socket.close()
        self.connected = False
        print(f"[TcpSocket {self.conn_id}] Connection terminated")
