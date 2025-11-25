# src/meshtastic/utils/packet_decode.py

import struct
from typing import Any, Dict, Optional

# These would come from your proto handling layer
# For now, stub functions until you wire in protobuf definitions
def un_frame(buffer: bytes) -> bytes:
    """
    Strip framing bytes from a buffer.
    Placeholder: adjust to match Meshtastic framing rules.
    """
    # TODO: implement actual unframing logic
    return buffer


def get_protobufs(type_name: str):
    """
    Lookup a protobuf decoder by type name.
    Placeholder: integrate with protobuf definitions.
    """
    raise NotImplementedError("get_protobufs not yet implemented")


def get_decode_types():
    """
    Return iterable of (name, decoder) pairs for all known protobuf types.
    Placeholder: integrate with protobuf definitions.
    """
    return []


def inspect_unknown(buffer: bytes) -> list[Dict[str, Any]]:
    """
    Inspect unknown buffer fields by reading tags and wire types.
    Equivalent to JS inspectUnknown.
    """
    stripped = un_frame(buffer)
    fields = []
    reader = memoryview(stripped)
    pos = 0
    length = len(reader)

    while pos < length:
        # Read varint tag
        tag = reader[pos]
        pos += 1
        field_num = tag >> 3
        wire_type = tag & 7
        fields.append({"fieldNum": field_num, "wireType": wire_type, "offset": pos})
        # Skip type (simplified; real implementation should handle wire types properly)
        pos += 1

    return fields


def try_decode_buf(buffer: bytes, type_name: str) -> Optional[Dict[str, Any]]:
    """
    Attempt to decode a buffer into a protobuf object of the given type.
    """
    try:
        decoder = get_protobufs(type_name)
        return decoder.decode(un_frame(buffer))
    except Exception:
        return None


def try_decode_all(buffer: bytes, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Try decoding buffer against all known types.
    """
    stripped = un_frame(buffer)
    meta = meta or {}

    for key, decoder in get_decode_types():
        try:
            decoded = decoder.decode(stripped)
            if decoded is None:
                break
            elif len(decoded.keys()) > 0:
                return {"type": key, **decoded, **meta}
            else:
                return {"type": key, **meta}
        except Exception:
            continue

    return {"type": "Unknown"}


def to_node_id_string(num: int) -> str:
    """
    Convert a numeric node ID to string form.
    """
    return "!" + format(num & 0xFFFFFFFF, "08x")


def decode_packet(buffer: bytes, source: str = "tcp", conn_id: str = "unknown") -> Dict[str, Any]:
    """
    Decode a packet from raw buffer.
    """
    return try_decode_all(buffer, {"source": source, "connId": conn_id})


def decode_from_radio_frame(frame: bytes) -> Optional[Dict[str, Any]]:
    """
    Decode a FromRadio frame.
    """
    buffer = un_frame(frame)
    data = try_decode_buf(buffer, "FromRadio")
    return data or None
