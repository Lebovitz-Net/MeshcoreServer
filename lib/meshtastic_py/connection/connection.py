# src/meshtastic/connection.py
import time
from typing import Any, Dict
from asyncio import Queue
from meshcore_py.events import EventEmitter
from protobufs.proto_decode import decode_from_radio_frame

class Connection(EventEmitter):
    mesh_runtime = None

    def __init__(self):
        super().__init__()
        self.conn_id = None
        self.meta_overrides: Dict[str, Any] = {}
        self._event_queue = Queue()

    @classmethod
    def bind_mesh_runtime(cls, runtime):
        cls.mesh_runtime = runtime

    def on_received_packet(self, meta: Dict[str, Any], buffer: bytes):

        try:
            frame = decode_from_radio_frame(buffer)
            if not frame:
                print("[on_packet_received] Failed to decode frame")
                return
            
            enriched_meta = {
                **meta,
                **self.meta_overrides,
                "connId": self.conn_id,
                "timestamp": int(time.time() * 1000),
            }

            # Re-emit for downstream consumers (optional)
            self.emit("ingest", frame, enriched_meta)
            self._event_queue.put_nowait((frame, enriched_meta))

        except Exception as err:
            print("[on_received_frame] Error ingesting packet:", err)

        # Instead of EventEmitter, we enqueue events


    async def next_event(self):
        """Async iterator for events."""
        return await self._event_queue.get()

    def send_packet(self, buffer: bytes):
        raise NotImplementedError("send_packet() must be implemented by subclass")

    def send(self, packet: bytes):
        if not Connection.mesh_runtime:
            raise RuntimeError("Mesh runtime not bound")
        Connection.mesh_runtime.send(packet)

    def want_config_id(self):
        from src.meshtastic.protobufs.proto_utils import build_to_radio_frame
        self.send(build_to_radio_frame("wantConfigId", 0))

    def send_message(self, text: str, to: int = None):
        from src.meshtastic.protobufs.proto_utils import build_text_message
        self.send(build_text_message({"message": text, "toNodeNum": to}))

    def request_telemetry(self):
        from src.meshtastic.protobufs.proto_utils import build_request_telemetry_frame
        self.send(build_request_telemetry_frame())

    def request_position(self):
        from src.meshtastic.protobufs.proto_utils import build_request_position_frame
        self.send(build_request_position_frame())

    def request_node_info(self):
        from src.meshtastic.protobufs.proto_utils import build_request_node_info_frame
        self.send(build_request_node_info_frame())
