# src/meshtastic/utils/node_mapping.py

import asyncio
from typing import Optional

# Mapping caches
_ip_to_device_map: dict[str, dict] = {}
_channel_to_num: dict[int, int] = {}
_mapping_waiters: dict[str, list[asyncio.Future]] = {}


def set_mapping(source_ip: str, num: int, device_id: str) -> None:
    """
    Set mapping for a source IP -> {num, device_id}.
    Resolves any pending waiters.
    """
    if not source_ip or not num:
        return

    _ip_to_device_map[source_ip] = {"num": num, "device_id": device_id}

    # Resolve any pending waiters
    if source_ip in _mapping_waiters:
        for fut in _mapping_waiters[source_ip]:
            if not fut.done():
                fut.set_result({"num": num, "device_id": device_id})
        del _mapping_waiters[source_ip]


def set_channel_mapping(channel_id: int, num: int) -> None:
    """
    Set mapping for a channel ID -> node number.
    """
    if channel_id is None or not num:
        return
    _channel_to_num[channel_id] = num


def get_mapping(source_ip: str) -> Optional[dict]:
    """
    Get mapping for a source IP.
    Returns None if not found.
    """
    return _ip_to_device_map.get(source_ip)


def get_channel_mapping(channel_id: int) -> Optional[int]:
    """
    Get node number for a channel ID.
    """
    return _channel_to_num.get(channel_id)


async def wait_for_mapping(source_ip: str, timeout: int = 5000) -> dict:
    """
    Awaitable mapping: waits until a mapping for source_ip is set.
    Raises TimeoutError if not resolved within timeout (ms).
    """
    existing = _ip_to_device_map.get(source_ip)
    if existing:
        return existing

    fut = asyncio.get_event_loop().create_future()
    if source_ip not in _mapping_waiters:
        _mapping_waiters[source_ip] = []
    _mapping_waiters[source_ip].append(fut)

    try:
        return await asyncio.wait_for(fut, timeout / 1000)
    except asyncio.TimeoutError:
        raise TimeoutError(f"Timeout waiting for mapping of {source_ip}")
