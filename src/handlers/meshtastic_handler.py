import asyncio
from meshcore_py import EventEmitter
from connection.tcp_connection import TcpConnection
from connection.serial_connection import SerialConnection
from src.meshtastic.meshtastic_ingestion_handler import MeshtasticIngestionHandler


class MeshtasticHandler(EventEmitter):
    def __init__(self, dispatcher, opts: dict = None):
        super().__init__()
        opts = opts or {}
        self.reconnect = opts.get("reconnect", {"enabled": True})
        self.get_config_on_connect = opts.get("get_config_on_connect", False)
        self.dispatcher = dispatcher
        # Single TCP connection
        self.connection = TcpConnection()
        self.ingestion_handler = MeshtasticIngestionHandler(dispatcher, self.on, self.off)

        # Serial connection
        self.serial_conn = SerialConnection("/dev/ttyUSB0", 115200, "serial-1")

        # Subscribe to packet events
        for conn in [self.connection, self.serial_conn]:
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

    # --- Shutdown ---
    def shutdown(self):
        """Gracefully shutdown TCP and Serial connections, then close handler."""
        print("[MeshtasticHandler] Shutting down...")
        if self.ingestion_handler:
            try:
                self.ingestion_handler.detach()
                print("[MeshtasticHandler] Ingestion handler detached.")
            except Exception as e:
                print(f"[MeshtasticHandler] Error detaching ingestion handler: {e}")
            finally:
                self.ingestion_handler = None
                
        # TCP connection
        if self.connection:
            try:
                self.connection.shutdown()
                print("[MeshtasticHandler] TCP connection shut down.")
            except Exception as e:
                print(f"[MeshtasticHandler] Error shutting down TCP connection: {e}")
            finally:
                self.connection = None

        # Serial connection
        if self.serial_conn:
            try:
                self.serial_conn.shutdown()
                print("[MeshtasticHandler] Serial connection shut down.")
            except Exception as e:
                print(f"[MeshtasticHandler] Error shutting down serial connection: {e}")
            finally:
                self.serial_conn = None

        # Close event emitter
        try:
            super().close()
            print("[MeshtasticHandler] EventEmitter closed.")
        except Exception as e:
            print(f"[MeshtasticHandler] Error closing EventEmitter: {e}")

        print("[MeshtasticHandler] Shutdown complete.")
