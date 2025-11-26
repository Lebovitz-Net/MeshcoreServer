# packet_router.py
from routing.dispatch_packet import dispatch_packet
from packet_decode import decode_packet
from utils.node_mapping import get_mapping
from utils.proto_utils import get_protobuf_types

def enrich_meta(value: dict = None, meta: dict = None):
    ts = int(__import__("time").time() * 1000)
    mapping = get_mapping(meta.get("sourceIp"))
    return {
        **(meta or {}),
        "timestamp": ts,
        "fromNodeNum": value.get("from") or meta.get("fromNodeNum") or mapping.get("num"),
        "toNodeNum": value.get("to") or meta.get("toNodeNum") or 0xFFFFFFFF,
        "device_id": meta.get("sourceIp") or mapping.get("device_id"),
    }

def route_packet(input, meta: dict = None):
    diag_packet = None
    try:
        data = decode_packet(input, meta.get("source"), meta.get("connId")) if isinstance(input, (bytes, bytearray)) else input
        if not data or data.get("type") == "Unknown":
            return
        oneofs = get_protobuf_types(data["type"])
        if oneofs:
            for key, value in data.items():
                if value is not None and oneofs.has(key):
                    diag_packet = data
                    dispatch_packet({"type": key, "data": data, "meta": enrich_meta(value, meta)})
        else:
            diag_packet = data
            dispatch_packet({"type": data["type"], "data": data, "meta": enrich_meta(data, meta)})
    except Exception as err:
        print("[routePacket] Failed to route packet:", err, diag_packet)
