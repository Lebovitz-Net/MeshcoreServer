import asyncio
from events.event_emitter import EventEmitter
from meshtastic.tcp_connection import TcpConnection
from meshtastic.serial_connection import SerialConnection


class MeshtasticHandler(EventEmitter):
    def __init__(self, conn_id: str, host: str, port: int, opts: dict = None):
        super().__init__()
        opts = opts or {}
        reconnect = opts.get("reconnect", {"enabled": True})
        get_config_on_connect = opts.get("getConfigOnConnect", False)

        # Primary TCP connection
        self.connection = TcpConnection({
            "connId": conn_id,
            "host": host,
            "port": port,
            "reconnectPolicy": reconnect.get("enabled", True),
        })

        # Additional transports (optional)
        self.tcp_conn = TcpConnection({"connId": conn_id, "host": host, "port": port})
        self.serial_conn = SerialConnection({
            "devicePath": "/dev/ttyUSB0",
            "baudRate": 115200,
            "connId": "serial-1",
        })

        # Subscribe to packet events
        for conn in [self.tcp_conn, self.serial_conn]:
            conn.on("packet", self._handle_packet)
            conn.on("connect", lambda meta: print(f"[Bridge] Connected: {meta}"))
            conn.on("error", lambda meta, err: print(f"[Bridge] Error: {meta}, {err}"))

    def _handle_packet(self, meta, buffer: bytes):
        """
        Handle incoming packets directly here instead of routing through meshGateway.
        Consumers can subscribe to 'packet' events on this handler.
        """
        self.emit("packet", meta, buffer)

    def send(self, packet: bytes):
        if isinstance(packet, (bytes, bytearray)):
            self.connection.write(packet)
        else:
            raise TypeError("[MeshtasticHandler] send packet must be bytes")

    def end(self):
        self.connection.stop()

    # Convenience wrappers for event subscription
    def on(self, event_name, callback):
        return super().on(event_name, callback)

    def off(self, event_name, callback):
        return super().off(event_name, callback)
