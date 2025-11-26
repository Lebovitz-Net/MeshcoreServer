import os
import uuid
import asyncio

from handlers.meshcore_handler import MeshcoreHandler
from meshcore.meshcore_requests import bind_mesh_runtime as bind_meshcore_requests
# from core.mesh_gateway import register_mesh_runtime


async def start_meshcore():
    # --- Config ---
    host = os.getenv("MESHCORE_HOST", "192.168.2.79")
    port = int(os.getenv("MESHCORE_PORT", "5000"))
    mesh_params = {"connId": str(uuid.uuid4()), "host": host, "port": port}
    mesh_opts = {
        "getConfigOnConnect": False,  # we’ll handle init explicitly
        "reconnect": {"enabled": True},
    }

    # --- Handler ---
    meshcore = MeshcoreHandler(mesh_params, mesh_opts)
    request = meshcore.tcp.request

    # Bind request helpers
    bind_meshcore_requests(meshcore)

    # Register runtime with gateway
    # register_mesh_runtime("meshcore-1", "meshcore", meshcore)

    # --- Startup sequence ---
    try:
        await meshcore.connect(timeout=20000)
        await request.get_self_info()
        print("[meshcore-1] Connection complete")
    except Exception as err:
        print("[meshcore-1] Connection failed:", err)

    # Configure radio + advert
    await request.set_radio_params(910525, 62000, 7, 5)
    await request.set_advert_name("KD1MU")
    await request.set_advert_lat_long(42345096, -71121411)

    # Fetch runtime info
    await request.get_channels()
    await request.get_contacts()
    await request.get_waiting_messages()
    # Example: await request.send_channel_text_message(0, "Boston GMRS Club meshcore enthusiasts")
    # Example: await request.get_neighbours(bos4_repeater_pubkey)

    # Start advert loop
    request.start_loop("advert", lambda: request.send_flood_advert(), 3600000)
    await request.get_self_info()

    print("meshcore startup complete")
    return {
        "meshcore": meshcore,
        "request": request,
        "stoploop": lambda: request.stop_loop("advert"),
    }
