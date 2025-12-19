# src/meshtastic/protobuf/proto_encode.py

import time
import random
from .proto_utils import (
    frame,
    get_protobufs,
    serialize,
)

# Simple rolling message ID generator
_current_id = 1

def generate_new_id() -> int:
    """
    Generate a new 32-bit message ID.
    Rolls over at 0xFFFFFFFF.
    """
    global _current_id
    _current_id = (_current_id + 1) & 0xFFFFFFFF
    return _current_id


def encode_to_radio(obj: dict, include_header: bool = True) -> bytes:
    """
    Encode a ToRadio message with framing.
    """
    ToRadio = get_protobufs("ToRadio")
    if not ToRadio:
        raise RuntimeError("init_proto_types() not called or ToRadio missing")

    msg = ToRadio(**obj)
    return frame(serialize(msg), include_header)


def encode_text_message(data: dict) -> bytes:
    """
    Build and encode a text message wrapped in a MeshPacket → ToRadio.
    Applies sensible defaults for ack, hop limit, etc.
    """
    Data = get_protobufs("Data")
    MeshPacket = get_protobufs("MeshPacket")
    if not Data or not MeshPacket:
        raise RuntimeError("Data/MeshPacket missing; call init_proto_types()")

    # Construct the inner Data payload
    data_payload = Data(
        portnum=1,
        payload=data.get("message", "").encode("utf-8"),
        bitfield=1,
    )

    # Construct the MeshPacket wrapper
    mesh_packet_payload = MeshPacket(
        from_field=data.get("fromNodeNum", 0),
        to=data.get("toNodeNum", 0xFFFFFFFF),
        id=data.get("messageId", generate_new_id()),
        channel=data.get("channelNum", 0),
        wantAck=data.get("wantAck", True),
        priority=1,
        hopLimit=data.get("hopLimit", 7),
        rxTime=int(time.time()),
        viaMqtt=1,
        hopStart=1,
        decoded=data_payload,
    )

    # Wrap in ToRadio and frame
    return encode_to_radio({"packet": mesh_packet_payload})
