# src/meshtastic/handlers/meshtastic_ingestion_handler.py
from meshcore_py.events import EventEmitter
from protobufs.proto_decode import decode_from_radio_frame
from .node_mapping import get_mapping
from protobufs.proto_utils import deserialize, get_protobufs

class MeshtasticIngestionHandler(EventEmitter):
    """
    Event-driven ingestion handler.
    Subscribes to packet events from a MeshtasticHandler and routes them.
    """

    def __init__(self, dispatcher, on_fn, off_fn):
        super().__init__()
        self.dispatcher = dispatcher
        self.on_fn = on_fn
        self.off_fn = off_fn
        self.attach()

    def attach(self):
        self.on("packet", self.handle_packet)

    def detach(self):
        self.off("packet", self.handle_packet)

    def handle_packet(self, packet):
        print(f"Ingested packet: {packet}")

    def ingest(self, meta: dict, buffer: bytes):
        """
        Ingest a raw packet from the Meshtastic runtime.
        Decodes the frame and routes it into the packet pipeline.
        """
        try:
            frame = decode_from_radio_frame(buffer)
            if not frame:
                print("[meshtasticIngest] Failed to decode frame")
                return

            # Hand off to the router
            self.route_packet(frame, meta)

            # Re-emit for downstream consumers (optional)
            self.emit("ingest", frame, meta)

        except Exception as err:
            print("[meshtasticIngest] Error ingesting packet:", err)

    def enrich_meta(self, value: dict = None, meta: dict = None):
        ts = int(__import__("time").time() * 1000)
        mapping = get_mapping(meta.get("sourceIp"))
        return {
            **(meta or {}),
            "timestamp": ts,
            "fromNodeNum": value.get("from") or meta.get("fromNodeNum") or mapping.get("num"),
            "toNodeNum": value.get("to") or meta.get("toNodeNum") or 0xFFFFFFFF,
            "device_id": meta.get("sourceIp") or mapping.get("device_id"),
        }

    def route_packet(self, input, meta: dict = None):
        diag_packet = None
        try:
            # Decode into a protobuf object
            if isinstance(input, (bytes, bytearray)):
                # Assume meta["type"] tells us which class to use
                cls = get_protobufs(meta.get("type"))
                if not cls:
                    return
                data = deserialize(cls, input)
            else:
                data = input  # already a protobuf object

            if not data:
                return

            diag_packet = data
            desc = data.DESCRIPTOR

            # Handle oneofs
            for oneof in desc.oneofs:
                field = data.WhichOneof(oneof.name)
                if field:
                    value = getattr(data, field)
                    self.dispatcher.dispatch_packet({
                        "type": field,
                        "data": data,
                        "meta": self.enrich_meta(value, meta),
                    })
                    return

            # Fallback: dispatch by message type name
            self.dispatcher.dispatch_packet({
                "type": desc.name,
                "data": data,
                "meta": self.enrich_meta(data, meta),
            })

        except Exception as err:
            print("[routePacket] Failed to route packet:", err, diag_packet)
