# packet_encoder.py
from utils.proto_utils import get_protobufs

def encode_to_radio(obj: dict) -> bytes:
    to_radio = get_protobufs("ToRadio")
    if not to_radio:
        raise RuntimeError("Protobuf types not initialized — call init_proto_types() first")
    err = to_radio.verify(obj)
    if err:
        raise ValueError(err)
    packet = to_radio.create(obj)
    buffer = to_radio.encode(packet).finish()
    return bytes([0x94, 0xC3]) + buffer

def encode_text_message(data: dict) -> bytes:
    Data = get_protobufs("Data")
    data_payload = Data.create({
        "portnum": 1,
        "payload": bytes(data["message"], "utf-8"),
        "bitfield": 1,
    })
    MeshPacket = get_protobufs("MeshPacket")
    mesh_packet_payload = MeshPacket.create({
        "from": data["fromNodeNum"],
        "to": data["toNodeNum"],
        "id": data["messageId"],
        "channel": data["channelNum"],
        "wantAck": data.get("wantAck", True),
        "decoded": data_payload,
        "priority": 1,
        "hopLimit": 7,
    })
    return encode_to_radio({"packet": mesh_packet_payload})
