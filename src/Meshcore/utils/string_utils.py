# src/meshtastic/utils/short_name_decoder.py
import re

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

def string_to_unicode_points(s: str) -> str:
    """Convert a string into Unicode code points (e.g. 'Hello🌍' -> 'U+48 U+65 ...')."""
    return " ".join([f"U+{ord(ch):X}" for ch in s])

def decode_python_string(s: str) -> str:
    """
    Decode a Python-style hex escape string (e.g. '\\x48\\x65\\x6C\\x6C\\x6F').
    If no escapes are found, return the string unchanged.
    """
    if not isinstance(s, str):
        return s
    hex_matches = re.findall(r"\\x[0-9a-fA-F]{2}", s)
    if hex_matches:
        byte_values = [int(h[2:], 16) for h in hex_matches]
        return bytes(byte_values).decode("utf-8", errors="replace")
    return s

def decode_raw_utf8(utf_bytes: bytes) -> bytes:
    """Return raw UTF-8 bytes unchanged."""
    return utf_bytes

def decode_varint(buf: bytes, offset: int):
    """Decode a protobuf-style varint starting at offset."""
    result = 0
    shift = 0
    length = 0
    while True:
        byte = buf[offset + length]
        result |= (byte & 0x7F) << shift
        length += 1
        if (byte & 0x80) == 0:
            break
        shift += 7
    return result, length

def find_first_wire_type(buffer: bytes) -> int:
    """
    Scan for the first field with wireType=2 (length-delimited).
    Returns the offset or -1 if not found.
    """
    for i in range(len(buffer) - 2):
        byte = buffer[i]
        wire_type = byte & 0x07
        field_number = byte >> 3
        if field_number > 0 and wire_type == 2:
            try:
                length, len_bytes = decode_varint(buffer, i + 1)
                total_length = i + 1 + len_bytes + length
                if total_length <= len(buffer):
                    return i
            except Exception:
                continue
    return -1

def get_field_name(n: int) -> str:
    return {
        1: "hexId",
        2: "longName",
        3: "shortName",
        4: "signature",
    }.get(n, f"field_{n}")

def decode_node_info(buffer: bytes) -> dict:
    """
    Decode a NodeInfo payload from a raw buffer.
    Extracts nodeId and fields (hexId, longName, shortName, signature).
    """
    if not isinstance(buffer, (bytes, bytearray)):
        raise TypeError("Expected a bytes-like object")

    payload_start = find_first_wire_type(buffer)
    if payload_start == -1:
        raise ValueError("No valid wire-type tag found")

    node_id = buffer[:payload_start].decode("utf-8", errors="replace")
    payload = buffer[payload_start:]

    fields = {}
    offset = 0
    while offset < len(payload):
        key_byte = payload[offset]
        offset += 1
        field_number = key_byte >> 3
        wire_type = key_byte & 0x07

        if wire_type != 2:
            fields[f"field_{field_number}"] = f"(unsupported wireType {wire_type})"
            break

        length, len_bytes = decode_varint(payload, offset)
        offset += len_bytes
        value_buf = payload[offset:offset + length]
        offset += length

        if field_number in (1, 4):
            value = value_buf.hex()
        elif field_number in (2, 3):
            value = value_buf.decode("utf-8", errors="replace")
        else:
            fields[f"field_{field_number}"] = f"(uninterpreted field {field_number})"
            continue

        fields[get_field_name(field_number)] = value

    return {"nodeId": node_id, **fields}
