# src/meshtastic/utils/node_mapping.py

import asyncio
from typing import Dict, List, Optional, Union
from asyncio import Future
from asyncio import get_running_loop

_ip_to_device_map: Dict[str, Dict[str, Union[int, str]]] = {}
_channel_to_num: Dict[int, int] = {}
_mapping_waiters: Dict[str, List[Future]] = {}


def set_mapping(source_ip: str, num: int, device_id: str) -> None:
    if not source_ip or not num:
        return
    _ip_to_device_map[source_ip] = {"num": num, "device_id": device_id}
    if source_ip in _mapping_waiters:
        for fut in _mapping_waiters[source_ip]:
            if not fut.done():
                fut.set_result({"num": num, "device_id": device_id})
        del _mapping_waiters[source_ip]


def set_channel_mapping(channel_id: int, num: int) -> None:
    if channel_id is None or not num:
        return
    _channel_to_num[channel_id] = num


def get_mapping(source_ip: str) -> Optional[Dict[str, Union[int, str]]]:
    return _ip_to_device_map.get(source_ip)


def get_channel_mapping(channel_id: int) -> Optional[int]:
    return _channel_to_num.get(channel_id)


async def wait_for_mapping(source_ip: str, timeout: int = 5000) -> Dict[str, Union[int, str]]:
    existing = _ip_to_device_map.get(source_ip)
    if existing:
        return existing

    fut: Future = get_running_loop().create_future()
    _mapping_waiters.setdefault(source_ip, []).append(fut)

    try:
        return await asyncio.wait_for(fut, timeout / 1000)
    except asyncio.TimeoutError:
        raise TimeoutError(f"Timeout waiting for mapping of {source_ip}")
