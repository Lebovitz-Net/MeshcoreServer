import signal
import asyncio
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from config import config
from api.runtime_config_routes import router as runtime_config_router
from api.routes import register_routes
from sse import sse_router, sse_handler, shutdown as sse_shutdown
from handlers.websocket_handler import websocket_handler
from meshtastic.utils.proto_utils import init_proto_types
from meshcore_startup import start_meshcore
from meshtastic_startup import start_meshtastic
from mqtt_startup import start_mqtt_server
from events.websocket_emitter import shutdown as ws_shutdown
from api.services_manager import shutdown as services_shutdown


app = FastAPI()

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET", "POST"],
    allow_credentials=True,
)

# --- Routes ---
app.include_router(sse_router, prefix="/sse")
app.include_router(runtime_config_router, prefix="/api/v1/config")
register_routes(app)

@app.get("/")
async def root():
    return "MeshManager v2 is running"

@app.get("/sse/events")
async def sse_events():
    return await sse_handler()


# --- Startup ---
async def startup_event():
    await init_proto_types()
    global mesh, meshcore, mqtt_client
    # mesh = await start_meshtastic()
    meshcore = await start_meshcore()
    mqtt_client = await start_mqtt_server()

app.add_event_handler("startup", startup_event)


# --- WebSocket ---
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await websocket_handler(ws)


# --- Graceful Shutdown ---
def shutdown_handler(sig, frame):
    print(f"🔻 Received {sig}, shutting down...")

    if "mqtt_client" in globals() and mqtt_client:
        mqtt_client.disconnect()

    if "meshcore" in globals() and meshcore:
        meshcore["request"].close()
        if meshcore.get("stoploop"):
            meshcore["stoploop"]()

    if "mesh" in globals() and mesh:
        mesh.end()

    ws_shutdown()
    sse_shutdown()
    services_shutdown(sig)

signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=config.api.port)
