# src/meshtastic/utils/portnums.py
"""
Central registry of MeshCore portNum values used in meshBridgeServer.
"""

# Core MeshCore
port_nums = {
    "Advert": 0x00,
    "Ping": 0x01,
    "Data": 0x23,
    "PathLearn": 0x2F,

    # Contact & Identity (BaseChatMesh / Coretact conventions)
    "Contact": 0x21,
    "ContactAck": 0x24,
    "ContactRequest": 0x25,

    # Experimental / Custom
    "Telemetry": 0x30,
    "ContactSync": 0x31,
    "DebugOverlay": 0x32,
    "RegistryPush": 0x33,
}

# Reserved ranges
Reserved = {
    "Core": (0x00, 0x1F),
    "Identity": (0x20, 0x2F),
    "Experimental": (0x30, 0x3F),
    "Custom": (0x40, 0x7F),
    "Vendor": (0x80, 0xFF),
}

# Reverse lookup table
reverse_map = {val: key for key, val in port_nums.items() if isinstance(val, int)}

def get_name(port_num: int) -> str:
    """Return the symbolic name for a port number, or Unknown if not found."""
    return reverse_map.get(port_num, f"Unknown (0x{port_num:02x})")

def is_known(port_num: int) -> bool:
    """Check if a port number is registered."""
    return port_num in reverse_map

def is_custom(port_num: int) -> bool:
    """Check if a port number is in the custom/experimental range."""
    return 0x30 <= port_num <= 0x7F
