import os
import asyncio

from handlers.meshtastic_handler import create_mesh_handler
from Meshtastic.tcp_connection import TcpConnection
from core.mesh_gateway import register_mesh_runtime, subscribe_to_packets
from Meshtastic.meshtastic_ingestion_handler import ingest as meshtastic_ingest
from Meshtastic.packets.packet_builder import build_to_radio_frame
from routing.node_mapping import wait_for_mapping


async def start_meshtastic():
    # --- Config ---
    host = os.getenv("NODE_IP_HOST", "192.168.1.52")
    port = int(os.getenv("NODE_IP_PORT", "4403"))

    # --- Handler ---
    mesh = await create_mesh_handler(
        "mesh-1",
        host,
        port,
        {
            "reconnect": {"enabled": True},
            "getConfigOnConnect": False,  # we’ll handle init explicitly
        },
    )

    # Bind request helpers
    TcpConnection.bind_mesh_requests(mesh)

    # Register runtime with gateway
    register_mesh_runtime("mesh-1", "meshtastic", mesh)

    # Subscribe to packets for ingestion
    subscribe_to_packets("mesh-1", lambda meta, buffer: meshtastic_ingest(meta, buffer))

    # --- Startup sequence ---
    try:
        # Send wantConfigId
        mesh.send(build_to_radio_frame("wantConfigId", 0))

        # Wait for mapping to be populated for this host
        mapping = await wait_for_mapping(host, timeout=5000)
        print(f"[mesh-1] Startup sequence complete, mapping ready: {mapping}")
    except Exception as err:
        print("[mesh-1] Startup sequence failed:", err)

    return mesh
