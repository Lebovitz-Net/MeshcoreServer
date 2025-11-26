# src/meshtastic/tcp_connection.py
import uuid
from .connection import Connection
from .tcp_socket import TcpSocket
from .schedule_reconnect import schedule_reconnect

class TcpConnection(Connection):
    def __init__(self, host: str, port: int, conn_id: str = None):
        super().__init__("tcp", conn_id or str(uuid.uuid4()))
        self.host = host
        self.port = port
        self.tcp_connections = {}
        self.reconnect_policy = True
        self.is_shutting_down = False

    def connect(self, conn_id=None):
        conn_id = conn_id or self.conn_id
        tcp = TcpSocket(conn_id, self.host, self.port)
        self.tcp_connections[conn_id] = {
            "tcp": tcp,
            "host": self.host,
            "port": self.port,
            "reconnectTimer": None,
        }
        return tcp

    async def start(self):
        tcp = self.connect(self.conn_id)
        await tcp.connected_promise
        print(f"[TcpConnection {self.conn_id}] Startup complete")
        return tcp

    def stop(self):
        self.is_shutting_down = True
        for entry in self.tcp_connections.values():
            tcp = entry["tcp"]
            if entry["reconnectTimer"]:
                entry["reconnectTimer"].cancel()
            tcp.end()
        self.tcp_connections.clear()

    def write(self, buf: bytes, conn_id=None):
        conn_id = conn_id or self.conn_id
        entry = self.tcp_connections.get(conn_id)
        tcp = entry["tcp"] if entry else None
        if not tcp:
            return False
        tcp.write(buf)
        return True
