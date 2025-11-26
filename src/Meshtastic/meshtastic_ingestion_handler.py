# src/meshtastic/handlers/meshtastic_ingestion_handler.py
from meshtastic.packets.packet_decode import decode_from_radio_frame
from meshtastic.packets.packet_router import route_packet

def ingest(meta: dict, buffer: bytes):
    """
    Ingest a raw packet from the Meshtastic runtime.
    Decodes the frame and routes it into the packet pipeline.
    """
    try:
        frame = decode_from_radio_frame(buffer)
        if not frame:
            print("[meshtasticIngest] Failed to decode frame")
            return

        # Hand off to the router
        route_packet(frame, meta)

    except Exception as err:
        print("[meshtasticIngest] Error ingesting packet:", err)
