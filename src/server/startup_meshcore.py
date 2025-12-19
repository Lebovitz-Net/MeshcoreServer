# src/server/startup_meshcore.py

import os
from urllib import request
import uuid
import asyncio
import contextlib
import logging

from src.handlers.meshcore_handler import MeshcoreHandler
from asyncio import get_running_loop


async def start_meshcore(meshcore, request):
    # --- Config ---
    logging.info("[MeshCore(tm)] ===== STARTING UP MESHCORE =====")
    host = os.getenv("MESHCORE_HOST", "192.168.2.79")
    port = int(os.getenv("MESHCORE_PORT", "5000"))
    mesh_params = {"connId": str(uuid.uuid4()), "host": host, "port": port}
    mesh_opts = {
        "getConfigOnConnect": False,  # we’ll handle init explicitly
        "reconnect": {"enabled": True},
    }
    logging.info(f"setting up Meshcore server host {host} port {port}")

    # --- Handler ---
    meshcore.start_meshcore(mesh_params, mesh_opts)

    # Step 2: bind request helpers
    print (" staring up in meshcore ", request)
    # --- Startup sequence ---
    try:
        await meshcore.connect(host, port, timeout_ms=20000)
        await request.get_self_info()
        print("[meshcore-1] Connection complete")
    except Exception as err:
        print("[meshcore-1] Connection failed:", err)

    # Configure radio + advert
    await request.set_radio_params(910525, 62500, 7, 5)
    await request.set_tx_power(22)
    await request.set_advert_name("KD1MU")
    await request.set_advert_lat_long(42345096, -71121411)
    # print("REBOOT")
    # await request.reboot()
    # Fetch runtime info
    await request.get_channels()
    await request.get_contacts()
    await request.get_waiting_messages()
    # await request.set_channel(1, "#test", "")

    # Start advert loop
    request.start_loop("advert", lambda: request.send_flood_advert(), 3600000)
    await request.send_channel_text_message(1, "@[ackbot] this Brookline Node is Online")
    print("meshcore startup complete")
    return {
        "meshcore": meshcore,
        "request": request,
        "stoploop": lambda: request.stop_loop("advert"),
        "shutdown": lambda: shutdown_meshcore(meshcore),
    }


def shutdown_meshcore(meshcore: MeshcoreHandler):
    """Gracefully shutdown MeshcoreHandler and cleanup startup state."""
    print("[meshcore startup] Shutting down meshcore...")
    try:
        if meshcore:
            # Cancel reader task if running
            if hasattr(meshcore, "reader_task"):
                meshcore.reader_task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    get_running_loop().run_until_complete(meshcore.reader_task)
            meshcore.shutdown()
            print("[meshcore startup] MeshcoreHandler shut down.")
    except Exception as e:
        print(f"[meshcore startup] Error shutting down MeshcoreHandler: {e}")
    print("[meshcore startup] Shutdown complete.")
