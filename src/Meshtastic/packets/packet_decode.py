# packet_decode.py
import protobuf
from utils.proto_utils import unframe, get_protobufs, get_decode_types

def inspect_unknown(buffer: bytes):
    stripped = unframe(buffer)
    reader = protobuf.Reader.create(stripped)
    fields = []
    while reader.pos < reader.len:
        tag = reader.uint32()
        field_num = tag >> 3
        wire_type = tag & 7
        fields.append({"fieldNum": field_num, "wireType": wire_type, "offset": reader.pos})
        reader.skipType(wire_type)
    return fields

def try_decode_buf(buffer: bytes, type_name: str):
    try:
        return get_protobufs(type_name).decode(unframe(buffer))
    except Exception:
        return None

def try_decode_all(buffer: bytes, meta: dict = None):
    stripped = unframe(buffer)
    for key, value in get_decode_types().items():
        try:
            decoded = value.decode(stripped)
            if decoded and len(decoded.keys()) > 0:
                return {"type": key, **decoded, **(meta or {})}
        except Exception:
            continue
    return {"type": "Unknown"}

def to_node_id_string(num: int) -> str:
    return "!" + format(num & 0xFFFFFFFF, "08x")

def decode_packet(buffer: bytes, source="tcp", conn_id="unknown"):
    return try_decode_all(buffer, {"source": source, "connId": conn_id})

def decode_from_radio_frame(frame: bytes):
    buffer = unframe(frame)
    data = try_decode_buf(buffer, "FromRadio")
    return data or None
