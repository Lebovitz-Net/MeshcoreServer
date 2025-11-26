# packet_utils.py
import binascii
from typing import Any, Dict, List, Optional, Union

DEFAULT_SKIP_KEYS = ["payload", "data", "message"]

def normalize_buffers(
    obj: Any,
    path: Optional[List[Union[str, int]]] = None,
    skip_keys: Optional[List[str]] = None,
    encoding: str = "hex"
) -> Any:
    """
    Recursively convert buffers to strings except for keys that should stay raw.
    - Preserves raw buffers under keys in skip_keys (e.g., payload/data/message).
    - Encodes other buffers to hex by default.
    """
    path = path or []
    skip_keys = skip_keys or DEFAULT_SKIP_KEYS

    # Buffer-like
    if isinstance(obj, (bytes, bytearray, memoryview)):
        last_key = path[-1] if path else None
        if last_key in skip_keys:
            return bytes(obj)  # preserve raw buffer for downstream decoding
        if encoding == "hex":
            return binascii.hexlify(bytes(obj)).decode()
        elif encoding == "utf-8":
            try:
                return bytes(obj).decode("utf-8")
            except Exception:
                return binascii.hexlify(bytes(obj)).decode()
        else:
            return binascii.hexlify(bytes(obj)).decode()

    # List/tuple
    if isinstance(obj, (list, tuple)):
        return [normalize_buffers(item, path + [i], skip_keys, encoding) for i, item in enumerate(obj)]

    # Dict
    if isinstance(obj, dict):
        return {k: normalize_buffers(v, path + [k], skip_keys, encoding) for k, v in obj.items()}

    return obj


def parse_plain_message(buffer: Union[bytes, bytearray, memoryview]) -> Optional[str]:
    """
    Attempt to decode a text buffer as UTF-8, falling back gracefully.
    """
    try:
        return bytes(buffer).decode("utf-8")
    except Exception as err:
        print("[parsePlainMessage] Failed to parse buffer:", err)
        return None


def get_channel(packet: Dict[str, Any]) -> Dict[str, int]:
    """
    Always returns a top-level 'channel' field (default 0).
    """
    channel = packet.get("channel")
    return {"channel": channel if isinstance(channel, int) else 0}


def get_base_meta(packet: Dict[str, Any]) -> Dict[str, Any]:
    """
    Canonical meta derived from MeshPacket-like structures.
    - rxTime is seconds in Meshtastic; convert to ms if present.
    """
    import time
    rx_time = packet.get("rxTime")
    timestamp = int(rx_time * 1000) if isinstance(rx_time, (int, float)) else int(time.time() * 1000)
    return {
        "packetId": packet.get("id"),
        "fromNodeNum": packet.get("from"),
        "toNodeNum": packet.get("to"),
        "timestamp": timestamp,
        "viaMqtt": packet.get("viaMqtt"),
        "hopStart": packet.get("hopStart") or packet.get("hoptstart"),
        **get_channel(packet),
    }


def extract_oneof_subtypes(entry: Dict[str, Any], source_type: str, proto_json: Dict[str, Any]) -> List[str]:
    """
    Extracts valid oneof subtypes from a decoded packet entry.
    - source_type: 'fromRadio' or 'meshPacket'
    - proto_json: loaded proto.json schema with message oneof metadata
    Returns a list of keys present in the entry that belong to oneof groups.
    """
    type_map = {
        "fromRadio": "meshtastic.FromRadio",
        "meshPacket": "meshtastic.MeshPacket",
    }
    message_type = type_map.get(source_type)
    if not message_type or message_type not in proto_json:
        print(f"[extract_oneof_subtypes] Unknown sourceType or missing proto definition: {source_type}")
        return []

    oneof_fields = proto_json[message_type].get("oneof", [])
    present_keys: List[str] = []

    for oneof_group in oneof_fields:
        for field_name in oneof_group.get("oneof", []):
            if entry.get(field_name) is not None:
                present_keys.append(field_name)

    return present_keys


def construct_subpacket(entry: Dict[str, Any], subtype: str) -> Optional[Dict[str, Any]]:
    """
    Constructs a normalized subpacket object for routing.
    Combines canonical metadata with the embedded subtype payload.
    """
    if not entry or entry.get(subtype) is None:
        print(f"[construct_subpacket] Missing subtype payload: {subtype}")
        return None

    return {
        "type": subtype,
        "fromNodeNum": entry.get("fromNodeNum"),
        "toNodeNum": entry.get("toNodeNum"),
        "rxTime": entry.get("rxTime"),
        "connId": entry.get("connId"),
        "transportType": entry.get("transportType"),
        "raw": entry.get("raw"),
        "channelNum": entry.get("channelNum"),
        "hopLimit": entry.get("hopLimit"),
        "portNum": entry.get("portNum"),
        "rxSnr": entry.get("rxSnr"),
        "rxRssi": entry.get("rxRssi"),
        "rxDeviceId": entry.get("rxDeviceId"),
        "rxGatewayId": entry.get("rxGatewayId"),
        "rxSessionId": entry.get("rxSessionId"),
        "decodedBy": entry.get("decodedBy"),
        "tags": entry.get("tags"),
        "data": entry.get(subtype),
    }


def extract_canonical_fields(entry: Dict[str, Any]) -> Dict[str, Any]:
    """
    Pulls a canonical subset of commonly used fields from any decoded packet entry.
    This mirrors the intent of getBaseMeta and augments with transport/diagnostic fields.
    """
    import time
    rx_time = entry.get("rxTime")
    timestamp = int(rx_time * 1000) if isinstance(rx_time, (int, float)) else int(time.time() * 1000)
    return {
        "fromNodeNum": entry.get("from") or entry.get("fromNodeNum"),
        "toNodeNum": entry.get("to") or entry.get("toNodeNum"),
        "rxTime": timestamp,
        "connId": entry.get("connId"),
        "transportType": entry.get("transportType"),
        "raw": entry.get("raw"),
        "channelNum": entry.get("channel") if isinstance(entry.get("channel"), int) else entry.get("channelNum"),
        "hopLimit": entry.get("hopLimit"),
        "portNum": entry.get("portnum") or entry.get("portNum"),
        "rxSnr": entry.get("rxSnr"),
        "rxRssi": entry.get("rxRssi"),
        "rxDeviceId": entry.get("rxDeviceId"),
        "rxGatewayId": entry.get("rxGatewayId"),
        "rxSessionId": entry.get("rxSessionId"),
        "decodedBy": entry.get("decodedBy"),
        "tags": entry.get("tags"),
    }


def normalize_decoded_packet(decoded: Union[Dict[str, Any], List[Dict[str, Any]]], proto_json: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Normalizes decoded packet(s) into enriched subpacket objects.
    Handles single or array input, extracts canonical fields,
    identifies oneof subtypes, and constructs dispatchable objects.
    """
    entries = decoded if isinstance(decoded, list) else [decoded]
    sub_packets: List[Dict[str, Any]] = []

    for entry in entries:
        source_type = entry.get("sourceType")
        if not source_type:
            print("[normalize_decoded_packet] Missing sourceType in decoded entry")
            continue

        canonical_fields = extract_canonical_fields(entry)
        subtypes = extract_oneof_subtypes(entry, source_type, proto_json)

        for subtype in subtypes:
            sub_packet = construct_subpacket({**entry, **canonical_fields}, subtype)
            if sub_packet:
                sub_packets.append(sub_packet)

    return sub_packets
