# src/meshtastic/serial_connection.py
import asyncio
import serial
import uuid
from .connection import Connection
from .schedule_reconnect import schedule_reconnect

class SerialConnection(Connection):
    def __init__(self, device_path: str, baud_rate: int, conn_id: str = None):
        super().__init__("serial", conn_id or str(uuid.uuid4()))
        self.device_path = device_path
        self.baud_rate = baud_rate
        self.serial_connections = {}
        self.reconnect_policy = True
        self.is_shutting_down = False

    def connect(self, conn_id=None):
        conn_id = conn_id or self.conn_id
        port = serial.Serial(self.device_path, self.baud_rate)
        self.serial_connections[conn_id] = {
            "port": port,
            "devicePath": self.device_path,
            "baudRate": self.baud_rate,
            "reconnectTimer": None,
        }
        return port

    async def start(self):
        port = self.connect(self.conn_id)
        await asyncio.sleep(0.1)  # simulate open
        print(f"[SerialConnection {self.conn_id}] Startup complete")
        return port

    def stop(self):
        self.is_shutting_down = True
        for entry in self.serial_connections.values():
            port = entry["port"]
            if entry["reconnectTimer"]:
                entry["reconnectTimer"].cancel()
            port.close()
        self.serial_connections.clear()

    def write(self, buf: bytes, conn_id=None):
        conn_id = conn_id or self.conn_id
        entry = self.serial_connections.get(conn_id)
        port = entry["port"] if entry else None
        if not port:
            return False
        port.write(buf)
        return True
