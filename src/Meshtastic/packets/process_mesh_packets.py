from src.meshtastic.utils.portnum_utils import get_port_name
from src.meshtastic.utils.decompress import decompress
from src.meshtastic.utils.packet_utils import parse_plain_message, get_base_meta, get_channel
from src.meshtastic.utils.packet_decode import try_decode_buf
from routing.dispatch_packet import dispatch_packet


def process_mesh_packet(packet: dict):
    data = packet.get("data", {})
    decoded = data.get("decoded", {})
    portnum = decoded.get("portnum")
    payload = decoded.get("payload")

    if not portnum or not payload:
        return None

    def extract_options(pkt: dict):
        msg = pkt.get("decode", {})
        return {
            "wantAck": msg.get("wantAck", 0),
            "wantReply": msg.get("wantResponse", 0),
            "replyId": msg.get("replyId", 0),
        }

    port_name = get_port_name(portnum)

    if port_name == "TEXT_MESSAGE_APP":
        message = parse_plain_message(payload)
        if message:
            dispatch_packet({
                "type": "message",
                "packet": packet,
                "meta": {**get_base_meta(data)},
            })

    elif port_name == "TEXT_MESSAGE_COMPRESSED_APP":
        try:
            decompressed = decompress(payload)
            if not decompressed:
                return None
            message = parse_plain_message(decompressed)
            if message:
                dispatch_packet({
                    "type": "message",
                    "data": {"packet": packet, **extract_options(packet)},
                    "meta": {**get_base_meta(data)},
                })
        except Exception as err:
            print("[dispatchMeshPacket] Port 7 decompression failed:", err)
            return None

    elif port_name == "POSITION_APP":
        position = try_decode_buf(payload, "Position")
        if position:
            dispatch_packet({
                "type": "position",
                "data": {
                    "latitude": position["latitudeI"] / 1e7,
                    "longitude": position["longitudeI"] / 1e7,
                    "altitude": position.get("altitude"),
                    "batteryLevel": position.get("batteryLevel"),
                    "toNodeNum": get_base_meta(data)["toNodeNum"],
                    "fromNodeNum": get_base_meta(data)["fromNodeNum"],
                },
                "meta": get_base_meta(data),
            })
        else:
            print("[dispatchMeshPacket] cannot decode Position")

    elif port_name == "NODEINFO_APP":
        user = try_decode_buf(payload, "User")
        if user:
            dispatch_packet({
                "type": "nodeInfo",
                "data": {
                    "id": user.get("id"),
                    "longName": user.get("longName"),
                    "shortName": user.get("shortName"),
                    "hwModel": user.get("hwModel"),
                },
                "meta": get_base_meta(data),
            })
        else:
            print("[dispatchMeshPacket] Failed to decode NodeInfo")

    elif port_name == "ROUTING_APP":
        dispatch_packet({
            "type": "routingMessage",
            "data": {"ignored": True},
            "meta": get_base_meta(data),
        })

    elif port_name == "ADMIN_APP":
        dispatch_packet({
            "type": "adminMessage",
            "data": {"ignored": True},
            "meta": get_base_meta(data),
        })

    elif port_name == "TELEMETRY_APP":
        telemetry = try_decode_buf(payload, "Telemetry")
        if telemetry:
            dispatch_packet({
                "type": "telemetry",
                "data": {
                    "voltage": telemetry.get("voltage"),
                    "channelUtilization": telemetry.get("channelUtilization"),
                    "airUtilTx": telemetry.get("airUtilTx"),
                },
                "meta": {**get_base_meta(data)},
            })
        else:
            print("[dispatchMeshPacket] Failed to decode Telemetry")

    else:
        print(
            f"[dispatchMeshPacket] Unknown port {portnum} on channel {get_channel(packet)}, skipping"
        )
