# packet_builder.py
import random
from utils.proto_utils import get_protobufs, START1, START2
from packet_encoder import encode_text_message

_current_id = 1

def generate_new_id():
    global _current_id
    _current_id = (_current_id + 1) & 0xFFFFFFFF
    return _current_id

def frame(bytes_data: bytes, include_header: bool = True) -> bytes:
    if not include_header:
        return bytes_data
    length = len(bytes_data)
    header = bytes([START1, START2, (length >> 8) & 0xFF, length & 0xFF])
    return header + bytes_data

def unframe(buf: bytes) -> bytes:
    return buf[2:] if buf and buf[0] == START1 and buf[1] == START2 else buf

def build_to_radio_frame(field_name: str, value, include_header: bool = True):
    ToRadio = get_protobufs("ToRadio")
    if not ToRadio or not hasattr(ToRadio, "fields") or field_name not in ToRadio.fields:
        print(f"Invalid fieldName: {field_name} not in ToRadio.oneof")
        return None
    msg = ToRadio.create({field_name: value})
    encoded = ToRadio.encode(msg).finish()
    return frame(encoded, include_header)

def build_text_message(packet: dict, opts: dict = None):
    send_buf = {
        "messageId": packet.get("messageId"),
        "channelId": packet.get("channelNum"),
        "fromNodeNum": packet.get("fromNodeNum"),
        "toNodeNum": packet.get("toNodeNum", 0xFFFFFFFF),
        "message": packet.get("message", ""),
        "wantAck": True,
        "wantReply": False,
        "replyId": None,
        "timestamp": int(random.random() * 1000),
    }
    return encode_text_message(send_buf)
