# src/meshtastic/schedule_reconnect.py
import asyncio

def schedule_reconnect(conn_id, host, port, connections, open_connection):
    entry = connections.get(conn_id)
    if not entry or entry.get("reconnectTimer"):
        return
    async def reconnect():
        await asyncio.sleep(3)
        entry["reconnectTimer"] = None
        open_connection(conn_id)
    entry["reconnectTimer"] = asyncio.create_task(reconnect())
