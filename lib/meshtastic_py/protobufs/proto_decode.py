# src/meshtastic/protobuf/proto_decode.py

from typing import Optional, Dict, Any
from .proto_utils import (
    unframe,
    extract_frames,
    get_protobufs,
    get_decode_types,
    deserialize,
    message_to_dict,
)

def inspect_unknown(buffer: bytes) -> list[Dict[str, Any]]:
    """
    Inspect unknown buffer fields by reading tags and wire types.
    Useful for debugging when a payload doesn't match known protobufs.
    """
    stripped = unframe(buffer)
    fields = []
    reader = memoryview(stripped)
    pos = 0
    length = len(reader)

    while pos < length:
        tag = reader[pos]
        pos += 1
        field_num = tag >> 3
        wire_type = tag & 7
        fields.append({"fieldNum": field_num, "wireType": wire_type, "offset": pos})
        pos += 1  # simplified skip
    return fields


def try_decode_buf(buffer: bytes, type_name: str) -> Optional[Dict[str, Any]]:
    """
    Attempt to decode a buffer into a protobuf object of the given type.
    """
    cls = get_protobufs(type_name)
    if not cls:
        return None
    try:
        msg = deserialize(cls, unframe(buffer))
        return message_to_dict(msg)
    except Exception:
        return None


def try_decode_all(buffer: bytes, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Try decoding buffer against all known protobuf types.
    Returns the first successful decode with type name and metadata.
    """
    stripped = unframe(buffer)
    meta = meta or {}

    for key, cls in get_decode_types():
        try:
            msg = deserialize(cls, stripped)
            decoded = message_to_dict(msg)
            if decoded:
                return {"type": key, **decoded, **meta}
        except Exception:
            continue

    return {"type": "Unknown", **meta}


def decode_packet(buffer: bytes, source: str = "tcp", conn_id: str = "unknown") -> Dict[str, Any]:
    """
    Public entry point for routing/dispatch.
    Decodes a single buffer into a protobuf dict, or marks as Unknown.
    """
    return try_decode_all(buffer, {"source": source, "connId": conn_id})


def decode_from_radio_frame(frame: bytes) -> Optional[Dict[str, Any]]:
    """
    Decode a FromRadio frame specifically.
    """
    return try_decode_buf(frame, "FromRadio")


def decode_stream(buffer: bytes, source: str = "tcp", conn_id: str = "unknown") -> list[Dict[str, Any]]:
    """
    Decode a stream of concatenated frames into a list of decoded packets.
    Uses extract_frames to split the stream.
    """
    results = []
    parsed = extract_frames(buffer)
    for frame in parsed["frames"]:
        results.append(decode_packet(frame, source=source, conn_id=conn_id))
    if parsed["remainder"]:
        results.append({"type": "IncompleteFrame", "raw": parsed["remainder"], "source": source, "connId": conn_id})
    return results
