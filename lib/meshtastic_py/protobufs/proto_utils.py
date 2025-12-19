# src/meshtastic/protobuf/proto_utils.py

import time
import sys
import os

from google.protobuf.json_format import MessageToDict

current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
sys.path.insert(0, current_dir)

# Import all generated protobuf modules
from .meshtastic import (
    mesh_pb2,
    channel_pb2,
    config_pb2,
    device_ui_pb2,
    module_config_pb2,
    portnums_pb2,
    telemetry_pb2,
    xmodem_pb2,
)

# Frame header constants
START1 = 0x94
START2 = 0xC3

# Global protobuf type map
mesh_map: dict[str, type] = {}

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


# ---------------------------
# Framing helpers
# ---------------------------

# src/meshtastic/protobuf/proto_utils.py

# ... existing code ...

from meshtastic import mesh_pb2

from meshtastic import mesh_pb2

def build_to_radio_frame(field_name: str) -> bytes:
    """
    Build a ToRadio protobuf with a single field set by name.
    For numeric fields, assigns the field number as the value.
    For string fields, assigns the field name itself.
    (Customize the assignment strategy as needed.)

    Args:
        field_name: The protobuf field name (e.g., "want_config_id").

    Returns:
        bytes: Framed, serialized ToRadio message.
    """
    to_radio = mesh_pb2.ToRadio()
    desc = mesh_pb2.ToRadio.DESCRIPTOR

    # Validate the field
    try:
        field = desc.fields_by_name[field_name]
    except KeyError:
        raise ValueError(f"Unknown field on ToRadio: {field_name}")

    # Decide assignment based on field type
    # You asked specifically to "look up the number and do the assignment"
    # for want_config_id (which is uint32). We generalize this:
    if field.type == field.TYPE_MESSAGE:
        raise TypeError(f"Field '{field_name}' is a message type; "
                        f"pass an instance of {field.message_type.name} instead.")

    elif field.type in (field.TYPE_UINT32, field.TYPE_INT32,
                        field.TYPE_INT64, field.TYPE_UINT64,
                        field.TYPE_SINT32, field.TYPE_SINT64,
                        field.TYPE_FIXED32, field.TYPE_FIXED64,
                        field.TYPE_SFIXED32, field.TYPE_SFIXED64):
        # Assign the field number as the value (e.g., want_config_id = 3)
        setattr(to_radio, field_name, field.number)

    elif field.type == field.TYPE_STRING:
        # Assign the field name itself (customize if you prefer a different default)
        setattr(to_radio, field_name, field_name)

    elif field.type == field.TYPE_BOOL:
        setattr(to_radio, field_name, True)

    elif field.type == field.TYPE_BYTES:
        setattr(to_radio, field_name, b"")

    else:
        raise TypeError(f"Unsupported field type for '{field_name}': {field.type}")

    serialized = to_radio.SerializeToString()
    return frame(serialized)




def frame(data: bytes, include_header: bool = True) -> bytes:
    """
    Add Meshtastic frame header (START1, START2, length).
    """
    if not include_header:
        return data
    length = len(data)
    header = bytes([START1, START2, (length >> 8) & 0xFF, length & 0xFF])
    return header + data


def unframe(buf: bytes) -> bytes:
    """
    Strip Meshtastic frame header if present.
    """
    if buf and buf[0] == START1 and buf[1] == START2:
        return buf[4:]
    return buf


def extract_frames(buffer: bytes, START1: int = START1, START2: int = START2):
    """
    Split a raw buffer into complete framed messages and any remainder.
    Useful for stream-oriented transports (TCP, serial).
    """
    frames = []
    working = bytearray(buffer)

    while len(working) >= 4:
        if working[0] != START1 or working[1] != START2:
            working = working[1:]
            continue

        frame_length = int.from_bytes(working[2:4], "big")
        total_length = 4 + frame_length

        if frame_length < 1 or frame_length > 4096 or len(working) < total_length:
            break

        frame = working[:total_length]
        frames.append(bytes(frame))
        working = working[total_length:]

    return {"frames": frames, "remainder": bytes(working)}


# ---------------------------
# Protobuf helpers
# ---------------------------

def _sort_order(val: str) -> int:
    """
    Deterministic ordering for key protobuf types.
    """
    order = {
        "FromRadio": 0,
        "ToRadio": 2,
        "MeshPacket": 3,
        "Config": 4,
        "ModuleConfig": 5,
    }
    return order.get(val, 30)


def init_proto_types() -> None:
    """
    Populate mesh_map by introspecting compiled classes
    from all imported protobuf modules.
    """
    modules = [
        mesh_pb2,
        channel_pb2,
        config_pb2,
        device_ui_pb2,
        module_config_pb2,
        portnums_pb2,
        telemetry_pb2,
        xmodem_pb2,
    ]

    candidates = []
    for module in modules:
        for name in dir(module):
            cls = getattr(module, name)
            if getattr(cls, "DESCRIPTOR", None) is not None:  # message classes
                candidates.append((name, cls))

    for name, cls in sorted(candidates, key=lambda x: _sort_order(x[0])):
        mesh_map[name] = cls


def get_protobufs(key: str):
    """Return protobuf class for a given type name."""
    return mesh_map.get(key)


def get_decode_types():
    """Return iterable of (name, class) pairs for all known protobuf types."""
    return [(k, v) for k, v in mesh_map.items() if v is not None]


def serialize(msg) -> bytes:
    """Serialize a protobuf message to bytes."""
    return msg.SerializeToString()


def deserialize(cls, buf: bytes):
    """Deserialize bytes into a protobuf message of type cls."""
    return cls.FromString(buf)


def message_to_dict(msg) -> dict:
    """Convert protobuf message to dict with original field names preserved."""
    return MessageToDict(msg, preserving_proto_field_name=True)
