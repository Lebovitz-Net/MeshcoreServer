# src/meshcore/decode_meshcore_packet.py

from external.meshcore_py.src.packets import Packet
from external.meshcore_py.src.packets import Decoders  # your existing decoder registry
from src.meshtastic.utils.proto_utils import un_frame


def try_decode_all(buffer: bytes, meta: dict | None = None) -> dict:
    """
    Attempt to decode a buffer using all registered MeshCore decoders.
    Returns a dict with type, payload, raw buffer, and metadata.
    """
    meta = meta or {}
    stripped = un_frame(buffer)

    for type_name, decode_fn in Decoders.items():
        if not callable(decode_fn):
            continue

        try:
            payload = decode_fn(stripped)
            if not payload or (isinstance(payload, dict) and len(payload) == 0):
                continue

            return {
                "type": type_name,       # inferred message type (e.g. 'SelfInfoResponse')
                "payload": payload,      # decoded object
                "raw": stripped,         # original buffer
                **meta                   # connId, timestamp, etc
            }
        except Exception:
            # Silent fail — decoder mismatch
            continue

    return {
        "type": "Unknown",
        "payload": None,
        "raw": stripped,
        **meta
    }


def decode_packet_with_message_type(frame: bytes, meta: dict | None = None) -> dict:
    """
    Decode a MeshCore packet frame and infer its message type.
    """
    meta = meta or {}
    packet = Packet.from_bytes(frame)

    base = {
        "route_type": packet.route_type_string,
        "payload_type": packet.payload_type_string,
        "payload_version": packet.payload_version,
        "connId": meta.get("connId"),
        "timestamp": meta.get("timestamp"),
        "source": meta.get("source", "meshcore"),
    }

    # Try to decode the inner payload
    decoded = try_decode_all(packet.payload, base)

    return {
        **base,
        "message_type": decoded["type"],        # e.g. 'SelfInfoResponse'
        "payload": decoded["payload"],          # decoded object
        "raw": decoded.get("raw") or packet.payload,  # raw buffer if unknown
    }
