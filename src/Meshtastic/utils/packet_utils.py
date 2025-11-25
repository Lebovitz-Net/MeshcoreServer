import datetime

DEFAULT_SKIP_KEYS = ["payload", "data", "message"]


def normalize_buffers(obj, path=None, skip_keys=DEFAULT_SKIP_KEYS, encoding="hex"):
    """
    Recursively normalize buffers into hex strings, except for keys we want to preserve raw.
    """
    if path is None:
        path = []

    # Handle bytes (Buffer equivalent)
    if isinstance(obj, (bytes, bytearray)):
        last_key = path[-1] if path else None
        if last_key in skip_keys:
            return obj  # preserve raw buffer for decoding
        return obj.hex() if encoding == "hex" else obj.decode(encoding, errors="ignore")

    # Handle lists
    if isinstance(obj, list):
        return [normalize_buffers(item, path + [i], skip_keys, encoding) for i, item in enumerate(obj)]

    # Handle dicts
    if isinstance(obj, dict):
        return {key: normalize_buffers(val, path + [key], skip_keys, encoding) for key, val in obj.items()}

    return obj


def parse_plain_message(buffer: bytes) -> str | None:
    """Decode a plain UTF-8 message payload."""
    try:
        return buffer.decode("utf-8").strip()
    except Exception as err:
        print("[parsePlainMessage] Failed to parse buffer:", err)
        return None


def get_channel(packet: dict) -> dict:
    """Always return a top-level channel field, defaulting to 0 if missing."""
    channel = 0
    if isinstance(packet.get("channel"), int):
        channel = packet["channel"]
    return {"channel": channel}


def get_base_meta(packet: dict) -> dict:
    """Construct canonical metadata for a packet."""
    return {
        "packetId": packet.get("id"),
        "fromNodeNum": packet.get("from"),
        "toNodeNum": packet.get("to"),
        "timestamp": (packet.get("rxTime") * 1000) if packet.get("rxTime") else int(datetime.datetime.now().timestamp() * 1000),
        "viaMqtt": packet.get("viaMqtt"),
        "hopStart": packet.get("hopStart"),
        **get_channel(packet),
    }


def extract_oneof_subtypes(entry: dict, source_type: str, proto_json: dict) -> list[str]:
    """
    Extract valid oneof subtypes from a decoded packet entry.
    Uses the sourceType to determine which proto message to inspect.
    """
    type_map = {
        "fromRadio": "meshtastic.FromRadio",
        "meshPacket": "meshtastic.MeshPacket",
    }

    message_type = type_map.get(source_type)
    if not message_type or message_type not in proto_json:
        print(f"Unknown sourceType or missing proto definition: {source_type}")
        return []

    oneof_fields = proto_json[message_type].get("oneof", [])
    present_keys = []

    for oneof_group in oneof_fields:
        for field_name in oneof_group.get("oneof", []):
            if entry.get(field_name) is not None:
                present_keys.append(field_name)

    return present_keys


def construct_sub_packet(entry: dict, subtype: str) -> dict | None:
    """
    Construct a normalized subpacket object for routing.
    Combines canonical metadata with the embedded subtype payload.
    """
    if not entry or subtype not in entry:
        print(f"Missing subtype payload: {subtype}")
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
        "data": entry[subtype],
    }


def normalize_decoded_packet(decoded: dict | list[dict], proto_json: dict) -> list[dict]:
    """
    Normalize decoded packet(s) into enriched subpacket objects.
    Handles single or array input, extracts canonical fields,
    identifies oneof subtypes, and constructs dispatchable objects.
    """
    entries = decoded if isinstance(decoded, list) else [decoded]
    print("[.../normalize] entries", entries)
    sub_packets = []

    for entry in entries:
        source_type = entry.get("sourceType")
        if not source_type:
            print("Missing sourceType in decoded entry")
            continue

        # canonicalFields would be another helper; stubbed here
        canonical_fields = {k: v for k, v in entry.items() if k not in ("data", "payload")}
        subtypes = extract_oneof_subtypes(entry, source_type, proto_json)

        for subtype in subtypes:
            sub_packet = construct_sub_packet({**entry, **canonical_fields}, subtype)
            if sub_packet:
                sub_packets.append(sub_packet)

    return sub_packets
