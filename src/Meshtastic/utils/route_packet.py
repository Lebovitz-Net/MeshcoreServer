# src/meshtastic/utils/route_packet.py

from src.meshtastic.utils.packet_decode import decode_packet
from src.meshtastic.utils.proto_utils import get_protobuf_types
from src.meshtastic.utils.node_mapping import get_mapping   # ✅ updated import
from src.dispatch_nodes import dispatch_packet


def enrich_meta(value: dict | None = None, meta: dict | None = None) -> dict:
    """
    Enrich metadata with timestamp, node IDs, and device ID.
    """
    import time
    value = value or {}
    meta = meta or {}
    ts = int(time.time() * 1000)  # ms timestamp
    mapping = get_mapping(meta.get("sourceIp"))

    return {
        **meta,
        "timestamp": ts,
        "fromNodeNum": (
            value.get("from")
            or meta.get("fromNodeNum")
            or value.get("fromNodeNum")
            or (mapping.get("num") if mapping else None)
        ),
        "toNodeNum": (
            value.get("to")
            or meta.get("toNodeNum")
            or value.get("toNodeNum")
            or 0xFFFFFFFF
        ),
        "device_id": meta.get("sourceIp") or (mapping.get("device_id") if mapping else None),
    }


def route_packet(input_data: bytes | dict, meta: dict | None = None) -> None:
    """
    Main entry point for decoded packet ingestion.
    Decomposes into subpackets, delegates decoding,
    enriches with context, and dispatches each to its handler.
    """
    meta = meta or {}
    diag_packet = None

    try:
        # Decode raw buffer if needed
        if isinstance(input_data, (bytes, bytearray)):
            data = decode_packet(input_data, meta.get("source"), meta.get("connId"))
        else:
            data = input_data

        if not data or data.get("type") == "Unknown":
            return

        oneofs = get_protobuf_types(data.get("type"))

        if oneofs:
            for key, value in data.items():
                if value is None:
                    continue
                if key not in oneofs:
                    continue

                diag_packet = data
                dispatch_packet({
                    "type": key,
                    "data": data,
                    "meta": enrich_meta(value, meta),
                })
        else:
            diag_packet = data
            dispatch_packet({
                "type": data.get("type"),
                "data": data,
                "meta": enrich_meta(data, meta),
            })

    except Exception as err:
        print("[routePacket] Failed to route packet:", err, diag_packet)
