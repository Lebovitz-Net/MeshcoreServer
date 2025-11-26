# src/sse.py
import asyncio
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

sse_router = APIRouter()

# Track connected clients
clients = []

async def event_generator(request: Request):
    """
    Async generator that yields events to the client.
    """
    queue = asyncio.Queue()
    clients.append(queue)

    # Send initial "Connected" event
    await queue.put("data: Connected\n\n")

    try:
        while True:
            # If client disconnects, break
            if await request.is_disconnected():
                break

            # Wait for next event
            try:
                event = await asyncio.wait_for(queue.get(), timeout=15.0)
                yield event
            except asyncio.TimeoutError:
                # Keep connection alive with a comment
                yield ": keep-alive\n\n"
    finally:
        clients.remove(queue)

@sse_router.get("/events")
async def sse_events(request: Request):
    """
    SSE endpoint: clients connect here to receive events.
    """
    return StreamingResponse(event_generator(request), media_type="text/event-stream")

# Broadcast function
def broadcast_event(event: dict):
    """
    Broadcast an event to all connected clients.
    """
    payload = f"data: {event}\n\n" if isinstance(event, str) else f"data: {event!r}\n\n"
    for queue in clients:
        queue.put_nowait(payload)

# Graceful shutdown
def shutdown():
    """
    Flush and clear all client queues.
    """
    for queue in clients:
        queue.put_nowait("data: Server shutting down\n\n")
    clients.clear()
