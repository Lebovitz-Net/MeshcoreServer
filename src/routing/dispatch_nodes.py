import json
from src.Utils.packet_utils import get_text_from_key, hash_public_key, get_public_key_value
from db.insert_handlers import insertHandlers
from overlays.overlay_emitter import emitOverlay
from events.event_emitter import emitEvent
from MeshCore.utils.string_utils import decode_node_info

# Convenience alias
insert_my_info = insertHandlers.insertMyInfo


def handle_self_info(packet):
    print(".../dispatch nodes selfInfo")
    data, meta = packet["data"]["data"], packet["data"]["meta"]

    shaped = {
        "id": data["name"],
        "myNodeNum": hash_public_key(data["publicKey"]),
        "type": data["type"],
        "name": data["name"],
        "publicKey": get_text_from_key(data["publicKey"]),
        "options": json.dumps({
            "txPower": data["txPower"],
            "maxTxPower": data["maxTxPower"],
            "advLat": data["advLat"],
            "advLon": data["advLon"],
            "reserved": data["reserved"],
            "manualAddContacts": data["manualAddContacts"],
            "radioFreq": data["radioFreq"],
            "radioBw": data["radioBw"],
            "radioSf": data["radioSf"],
            "radioCf": data["radioCf"],
        }),
        "protocol": "meshcore",
        **meta,
    }
    insert_my_info(shaped)


def handle_ok(packet):
    print(".../dispatchNodes Ok")


def handle_contact_msg_response(packet):
    data, meta = packet["data"], packet["meta"]
    d = data["data"]
    shaped = {
        "contactId": d["advName"],
        "nodeNum": hash_public_key(d["publicKey"]),
        "type": d.get("type"),
        "name": d["advName"],
        "shortName": None,
        "publicKey": d["publicKey"],
        "times": json.dumps({"lastAdvert": d["lastAdvert"], "lastMod": d.get("lastMod")}),
        "position": json.dumps({"advlat": d["advlat"], "advlon": d["advlon"]}),
        "path": json.dumps({"outPath": d["outPath"], "outPathLen": d["outPathLen"]}),
        "options": json.dumps({"flags": d["flags"]}),
        **meta,
    }
    # TODO: insertUser


def handle_my_node_info(sub_packet):
    print(".../MyNodeInfo ")


def handle_my_info(sub_packet):
    data, conn_id, timestamp, meta = sub_packet["data"], sub_packet["connId"], sub_packet.get("timestamp"), sub_packet["meta"]
    my_info = data["myInfo"]
    print(".../myNodeInfo ")

    result = insertHandlers.insertMyInfo({
        **my_info,
        "connId": conn_id,
        "currentIP": meta["sourceIp"],
        "timestamp": timestamp or meta["timestamp"],
    })


def handle_node_filter(sub_packet):
    data, meta = sub_packet["data"], sub_packet["meta"]
    print("[dispatchNodes] ... NodeFilter", sub_packet, decode_node_info(data["nodeName"]))


def handle_node_highlight(sub_packet):
    print("[dispatchNodes] ... NodeHighlight", sub_packet)


def handle_node_info(sub_packet):
    print("[dispatchNodes] ... NodeInfo", sub_packet)


def handle_node_info_detailed(sub_packet):
    data, meta = sub_packet["data"], sub_packet["meta"]
    num = data["num"]
    # TODO: shape nodeInfo, user, metrics, position
    print("[dispatchNodes] ... nodeInfo detailed")
    emitOverlay("lineage", sub_packet)
    emitEvent("configComplete", sub_packet)


def handle_position(sub_packet):
    data, meta = sub_packet["data"], sub_packet["meta"]
    pos = data["position"]

    insertHandlers.insertPosition({
        "fromNodeNum": data["fromNodeNum"],
        "toNodeNum": data["toNodeNum"],
        "latitude": data["latitude"],
        "longitude": data["longitude"],
        "altitude": data.get("altitude"),
        "sats_in_view": data.get("satsInView"),
        "batteryLevel": data.get("batteryLevel"),
        "device_id": meta["device_id"],
        "conn_id": meta["connId"],
        "timestamp": meta["timestamp"],
    })

    emitOverlay("position", sub_packet)
    emitEvent("locationUpdated", sub_packet)


def handle_waypoint(sub_packet):
    print("[dispatchNodes] ... Waypoint")


def handle_user(sub_packet):
    print("[dispatchNodes] ... User", sub_packet)


def handle_position_packet(packet):
    print("[dispatchNodes] ... Position")


# Registry of handlers
dispatchNodes = {
    "SelfInfo": handle_self_info,
    "Ok": handle_ok,
    "ContactMsgResponse": handle_contact_msg_response,
    "MyNodeInfo": handle_my_node_info,
    "myInfo": handle_my_info,
    "NodeFilter": handle_node_filter,
    "NodeHighlight": handle_node_highlight,
    "NodeInfo": handle_node_info,
    "nodeInfo": handle_node_info_detailed,
    "position": handle_position,
    "Waypoint": handle_waypoint,
    "User": handle_user,
    "Position": handle_position_packet,
}
