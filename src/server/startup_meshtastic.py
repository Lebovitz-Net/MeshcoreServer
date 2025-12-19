# src/startup/meshtastic_startup.py

import os
import asyncio
import logging
import uuid
from src.handlers.meshtastic_handler import MeshtasticHandler
from protobufs.proto_utils import build_to_radio_frame, init_proto_types
from src.meshtastic.node_mapping import wait_for_mapping

async def start_meshtastic(mesh: MeshtasticHandler, request):
    logging.info("[Meshtastic] ===== STARTING UP MESHTASTIC =====")
    init_proto_types()
    host = os.getenv("NODE_IP", "192.168.2.79")
    port = int(os.getenv("NODE_PORT", "4403"))
    mesh.connection.connect(conn_id=str(uuid.uuid4()), host=host, port=port)

    # Startup sequence...
    mesh.send(build_to_radio_frame("want_config_id"))
    try:
        mapping = await wait_for_mapping(host, timeout=5000)
    except TimeoutError:
        print(f"[mesh-1] Timeout waiting for node mapping for IP {host}")
        mapping = None
    
    print(f"[mesh-1] Startup complete, mapping ready: {mapping}")

    return mesh

def shutdown_meshtastic(mesh: MeshtasticHandler):
    """Gracefully shutdown Meshtastic handler (TCP + Serial)."""
    print("[MeshtasticStartup] Shutting down Meshtastic...")
    try:
        if mesh:
            mesh.shutdown()
            print("[MeshtasticStartup] Handler shut down.")
    except Exception as e:
        print(f"[MeshtasticStartup] Error during shutdown: {e}")
    print("[MeshtasticStartup] Shutdown complete.")
