# src/sse.py
from aiohttp import web
from aiohttp.web_exceptions import HTTPClientError
from aiohttp.client_exceptions import ClientConnectionError, ClientPayloadError, ClientConnectionResetError
import asyncio
import json
from meshcore_py import EventEmitter

class SSEEmitter(EventEmitter):
    def __init__(self, app: web.Application, path: str = "/events"):
        super().__init__()
        self._clients = set()
        self.app = app
        app.router.add_get(path, self.sse_events)
        self.setup_events()

    async def broadcast_event(self, event: dict):
        """Broadcast an event to all connected clients asynchronously."""
        payload = f"data: {json.dumps(event)}\n\n"
        dead_clients = []

        for queue in list(self._clients):
            try:
                await queue.put(payload)   # async put
            except Exception:
                dead_clients.append(queue)

        for queue in dead_clients:
            self._clients.discard(queue)

    def setup_events(self):
        # Register async handlers that forward events to SSE clients
        async def handle_node(node):
            await self.broadcast_event({"type": "node", "node": node})

        async def handle_channel(channel):
            await self.broadcast_event({"type": "channel", "channel": channel})

        async def handle_message(message):
            print(f".../SSE EMITTER Handling message")
            await self.broadcast_event({"type": "message", "message": message})

        self.on("node_updated", handle_node)
        self.on("channel_received", handle_channel)
        self.on("message_arrived", handle_message)
            
    async def event_generator(self, request, queue):
        """Async generator that yields SSE events to the client."""
        # Send initial event
        await queue.put("data: Connected\n\n")

        try:
            while True:
                if request.transport is None or request.transport.is_closing():
                    break

                try:
                    event = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield event.encode("utf-8")
                except asyncio.TimeoutError:
                    yield b": keep-alive\n\n"
        finally:
            self._clients.discard(queue)

    async def sse_events(self, request):
        response = web.StreamResponse(
            status=200,
            reason='OK',
            headers={
                'Content-Type': 'text/event-stream',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
            }
        )
        await response.prepare(request)

        # Create a queue for this client
        queue = asyncio.Queue()
        self._clients.add(queue)

        try:
            async for chunk in self.event_generator(request, queue):
                await response.write(chunk)
        except (ClientConnectionResetError, ClientConnectionError, ConnectionResetError, asyncio.CancelledError):
            print("SSE client disconnected")
        finally:
            self._clients.discard(queue)
            try:
                await response.write_eof()
            except Exception:
                pass

        return response


    def shutdown(self):
        """Flush and clear all client queues."""
        for queue in self._clients:
            queue.put_nowait("data: Server shutting down\n\n")
        self._clients.clear()
