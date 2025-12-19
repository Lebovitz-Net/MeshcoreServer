# src/meshtastic/utils/packet_utils.py
import binascii
import time
from typing import Any, Dict, List, Optional, Union
from protobufs.proto_utils import get_protobufs

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

    if isinstance(obj, (bytes, bytearray, memoryview)):
        last_key = path[-1] if path else None
        if last_key in skip_keys:
            return bytes(obj)
        if encoding == "hex":
            return binascii.hexlify(bytes(obj)).decode()
        elif encoding == "utf-8":
            try:
                return bytes(obj).decode("utf-8")
            except Exception:
                return binascii.hexlify(bytes(obj)).decode()
        return binascii.hexlify(bytes(obj)).decode()

    if isinstance(obj, (list, tuple)):
        return [normalize_buffers(item, path + [i], skip_keys, encoding) for i, item in enumerate(obj)]

    if isinstance(obj, dict):
        return {k: normalize_buffers(v, path + [k], skip_keys, encoding) for k, v in obj.items()}

    return obj


def parse_plain_message(buffer: Union[bytes, bytearray, memoryview]) -> Optional[str]:
    """Attempt to decode a text buffer as UTF-8, falling back gracefully."""
    try:
        return bytes(buffer).decode("utf-8")
    except Exception as err:
        print("[parsePlainMessage] Failed to parse buffer:", err)
        return None


def get_channel(packet: Dict[str, Any]) -> Dict[str, int]:
    """Always returns a top-level 'channel' field (default 0)."""
    channel = packet.get("channel")
    return {"channel": channel if isinstance(channel, int) else 0}


def get_base_meta(packet: Dict[str, Any]) -> Dict[str, Any]:
    """Canonical meta derived from MeshPacket-like structures."""
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


def extract_oneof_subtypes(entry: Dict[str, Any], type_name: str) -> List[str]:
    """
    Extract valid oneof subtypes from a decoded protobuf entry.
    Uses compiled descriptors instead of proto.json.
    """
    cls = get_protobufs(type_name)
    if not cls:
        return []

    present_keys: List[str] = []
    for oneof in cls.DESCRIPTOR.oneofs:
        for field in oneof.fields:
            if entry.get(field.name) is not None:
                present_keys.append(field.name)
    return present_keys


def construct_subpacket(entry: Dict[str, Any], subtype: str) -> Optional[Dict[str, Any]]:
    """Constructs a normalized subpacket object for routing."""
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
    """Pulls a canonical subset of commonly used fields from any decoded packet entry."""
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


def normalize_decoded_packet(decoded: Union[Dict[str, Any], List[Dict[str, Any]]], type_name: str) -> List[Dict[str, Any]]:
    """
    Normalizes decoded packet(s) into enriched subpacket objects.
    Handles single or array input, extracts canonical fields,
    identifies oneof subtypes, and constructs dispatchable objects.
    """
    entries = decoded if isinstance(decoded, list) else [decoded]
    sub_packets: List[Dict[str, Any]] = []

    for entry in entries:
        canonical_fields = extract_canonical_fields(entry)
        subtypes = extract_oneof_subtypes(entry, type_name)

        for subtype in subtypes:
            sub_packet = construct_subpacket({**entry, **canonical_fields}, subtype)
            if sub_packet:
                sub_packets.append(sub_packet)

    return sub_packets
