"""
General utilities for the server.
Includes timestamp normalization helpers.
"""

def normalize_in(time: int | float) -> int | float:
    """
    Normalize incoming time values.
    If time < 2_000_000_000, treat as seconds and convert to ms.
    Otherwise assume already ms.
    """
    return time * 1000 if time < 2_000_000_000 else time

def normalize_out(time: int | float) -> int | float:
    """
    Normalize outgoing time values.
    If time < 2_000_000_000, assume already seconds.
    Otherwise convert ms to seconds.
    """
    return time if time < 2_000_000_000 else time / 1000
