# src/routing/dispatch_utils.py
import re


def normalize_packet(packet):
    if "meta" in packet:
        # Meshtastic
        return {
            "packet_type": "meshtastic",
            "data": packet.get("data"),
            "meta": packet.get("meta"),
        }
    elif isinstance(packet.get("data"), dict) and "meta" in packet["data"]:
        # Meshcore
        inner = packet["data"]
        return {
            "packet_type": "meshcore",
            "data": inner.get("data"),
            "meta": inner.get("meta"),
        }
    else:
        # Unknown shape
        return {
            "packet_type": "unknown",
            "data": packet.get("data"),
            "meta": packet.get("meta"),
        }


def to_snake_case(key: str) -> str:
    """
    Normalize a type key to snake_case.

    - "CHANNEL_INFO" -> "channel_info"
    - "channel_info" -> "channel_info"
    - "ContactsStart" -> "contacts_start"
    - "MsgWaiting" -> "msg_waiting"
    - "queueStatus" -> "queue_status"
    """
    if not key:
        return key

    # If it's already UPPER_SNAKE_CASE, just lower it.
    if "_" in key and key.upper() == key:
        return key.lower()

    # General CamelCase / mixedCase -> snake_case
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", key)
    s2 = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1)
    return s2.lower()
