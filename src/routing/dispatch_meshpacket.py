from Meshtastic.packets.process_mesh_packet import process_mesh_packet


def handle_data(packet: dict):
    sub_packet = packet.get("data")
    # TODO: implement handling of Data sub-packet
    return sub_packet


def handle_decoded(packet: dict):
    # TODO: implement decoded packet handling
    pass


dispatchMeshPacket = {
    "MeshPacket": process_mesh_packet,
    "packet": process_mesh_packet,
    "Data": handle_data,
    "decoded": handle_decoded,
}
