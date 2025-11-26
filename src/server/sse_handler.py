# src/sse.py
import asyncio
import json
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

sse_router = APIRouter()
sse_clients = set()

async def event_stream(request: Request):
    """
    Async generator that streams events to the client.
    """
    queue = asyncio.Queue()
    sse_clients.add(queue)

    # Initial heartbeat (ping)
    await queue.put(f"data: {json.dumps({'type': 'ping', 'timestamp': int(asyncio.get_event_loop().time()*1000)})}\n\n")

    try:
        while True:
            if await request.is_disconnected():
                break
            try:
                event = await asyncio.wait_for(queue.get(), timeout=15.0)
                yield event
            except asyncio.TimeoutError:
                # Keep connection alive
                yield ": keep-alive\n\n"
    finally:
        sse_clients.remove(queue)

@sse_router.get("/events")
async def sse_handler(request: Request):
    """
    SSE endpoint: clients connect here to receive events.
    """
    return StreamingResponse(event_stream(request), media_type="text/event-stream")

def broadcast_event(event: dict):
    """
    Broadcast an event to all connected SSE clients.
    """
    payload = f"data: {json.dumps(event)}\n\n"
    for queue in list(sse_clients):
        queue.put_nowait(payload)

def shutdown():
    """
    Gracefully close all SSE client connections.
    """
    for queue in list(sse_clients):
        queue.put_nowait("data: Server shutting down\n\n")
    sse_clients.clear()
