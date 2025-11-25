# src/meshtastic/utils/proto_utils.py

import os
import hashlib
import random
import time
import netifaces
from google.protobuf import descriptor_pool, message_factory

START1 = 0x94
START2 = 0xC3

mesh_map = {}
pool = descriptor_pool.Default()
factory = message_factory.MessageFactory(pool)


def init_proto_types(proto_json: dict):
    top_level_protos = proto_json.get("nested", {}).get("meshtastic", {}).get("nested", {})
    mesh_proto_types = sorted(
        [
            key
            for key, val in top_level_protos.items()
            if "oneofs" in val and "payloadVariant" in val["oneofs"]
        ],
        key=_sort_order,
    )
    for type_name in mesh_proto_types:
        mesh_map[type_name] = None  # stub until you wire compiled protos


def _sort_order(val: str) -> int:
    if val == "FromRadio":
        return 0
    if val == "ToRadio":
        return 2
    if val == "MeshPacket":
        return 3
    if val == "Config":
        return 4
    if val == "ModuleConfig":
        return 5
    return 30


def get_protobufs(key: str):
    return mesh_map.get(key)


def get_protobuf_oneofs(type_name: str):
    proto = get_protobufs(type_name)
    if proto and hasattr(proto, "oneofs"):
        return getattr(proto.oneofs, "payloadVariant", {}).get("oneof", None)
    return None


def get_protobuf_types(type_name: str):
    oneofs = get_protobuf_oneofs(type_name)
    return set(oneofs) if oneofs else None


def get_decode_types():
    return mesh_map.items()


def get_mac_addresses():
    macs = []
    for iface in netifaces.interfaces():
        addrs = netifaces.ifaddresses(iface)
        if netifaces.AF_LINK in addrs:
            for link in addrs[netifaces.AF_LINK]:
                mac = link.get("addr")
                if mac and mac != "00:00:00:00:00:00":
                    macs.append(mac)
    return macs


def generate_node_num(seed_input: bytes | str | None = None) -> int:
    if seed_input:
        seed = seed_input.encode("utf-8") if isinstance(seed_input, str) else seed_input
    else:
        mac_list = get_mac_addresses()
        valid_mac = next((m for m in mac_list if m and m != "00:00:00:00:00:00"), None)
        if not valid_mac:
            raise RuntimeError("No valid MAC address found for fallback seed.")
        seed = bytes.fromhex(valid_mac.replace(":", ""))

    hash_bytes = hashlib.sha256(seed).digest()
    return int.from_bytes(hash_bytes[-4:], "big")


def frame(data: bytes, include_header: bool = True) -> bytes:
    if not include_header:
        return data
    length = len(data)
    header = bytes([START1, START2, (length >> 8) & 0xFF, length & 0xFF])
    return header + data


def un_frame(buf: bytes) -> bytes:
    if buf and buf[0] == START1 and buf[1] == START2:
        return buf[2:]
    return buf


def create_to_radio_frame(field_name: str, value: dict, opts: dict = None) -> bytes | None:
    opts = opts or {}
    types = get_protobuf_types("ToRadio")
    if not types or field_name not in types:
        print(f"Invalid fieldName: {field_name} not in ToRadio.oneof")
        return None

    ToRadio = get_protobufs("ToRadio")
    if not ToRadio:
        return None

    msg = ToRadio(**{field_name: value})
    encoded = msg.SerializeToString()
    return frame(encoded, opts.get("includeHeader", True))


def create_mesh_packet_frame(type_name: str, payload: bytes, opts: dict = None) -> bytes:
    opts = opts or {}
    MeshPacket = get_protobufs("MeshPacket")
    if not MeshPacket:
        return b""

    mesh = MeshPacket(
        from_field=opts.get("from", 0x1),
        to=opts.get("to", 0),
        channel=opts.get("channel", 0),
        id=opts.get("id", random.randint(0, 0xFFFFFFFF)),
        rxTime=int(time.time()),
        viaMqtt=1,
        hopStart=1,
        decoded=payload,
    )
    encoded = mesh.SerializeToString()
    return frame(encoded, opts.get("includeHeader", True))
