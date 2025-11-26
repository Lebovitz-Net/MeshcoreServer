import signal
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from config import config
from api.runtime_config_routes import router as runtime_config_router
from api.routes import register_routes
from sse import sse_router, sse_handler, shutdown as sse_shutdown
from meshtastic.utils.proto_utils import init_proto_types
from startup_meshcore import start_meshcore
from startup_meshtastic import start_meshtastic
from startup_mqtt import start_mqtt_server
from api.services_manager import shutdown as services_shutdown

# ✅ import global_state
from api.global_state import global_state

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
    # ✅ assign into global_state instead of raw globals
    # global_state.mesh = await start_meshtastic()   # enable if needed
    global_state.meshcore = await start_meshcore()
    global_state.mqtt_client = await start_mqtt_server()

app.add_event_handler("startup", startup_event)

# --- Graceful Shutdown ---
def shutdown_handler(sig, frame):
    print(f"🔻 Received {sig}, shutting down...")

    if global_state.mqtt_client:
        global_state.mqtt_client.disconnect()

    if global_state.meshcore:
        global_state.meshcore["request"].close()
        if global_state.meshcore.get("stoploop"):
            global_state.meshcore["stoploop"]()

    if global_state.mesh:
        global_state.mesh.end()

    sse_shutdown()
    services_shutdown(sig)

signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)

if __name__ == "__main__":
    # ✅ stash API server reference in global_state
    global_state.api_server = uvicorn.run(app, host="0.0.0.0", port=config.api.port)
