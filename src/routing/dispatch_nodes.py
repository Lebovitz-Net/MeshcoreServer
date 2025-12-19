# src/routing/dispatch_nodes.py

import json
from src.utils import get_text_from_key, hash_public_key, get_public_key_value
from src.meshcore.string_utils import decode_node_info

# Convenience alias


class DispatchNodes:
    def self_info(self, packet: dict):
        print(".../dispatchNodes SelfInfo")
        data, meta = packet["data"], packet["meta"]

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
                "reserved": data["reserved"].hex(),
                "manualAddContacts": data["manualAddContacts"],
                "radioFreq": data["radioFreq"],
                "radioBw": data["radioBw"],
                "radioSf": data["radioSf"],
                "radioCr": data["radioCr"],
            }),
            "protocol": "meshcore",
            **meta,
        }
        self.insert_handlers.insert_my_info(shaped)

    def ok(self, packet: dict):
        print(".../dispatchNodes Ok")

    def contact_msg_response(self, packet: dict):
        data, meta = packet["data"], packet["meta"]
        d = data
        shaped = {
            "contactId": d["advName"],
            "nodeNum": hash_public_key(d["publicKey"]),
            "type": d.get("type"),
            "name": d["advName"],
            "shortName": None,
            "publicKey": d["publicKey"],
            "times": json.dumps({
                "lastAdvert": d["lastAdvert"],
                "lastMod": d.get("lastMod"),
            }),
            "position": json.dumps({
                "advlat": d["advlat"],
                "advlon": d["advlon"],
            }),
            "path": json.dumps({
                "outPath": d["outPath"],
                "outPathLen": d["outPathLen"],
            }),
            "options": json.dumps({"flags": d["flags"]}),
            **meta,
        }
        # TODO: self.insert_handlers.insertUser(shaped)

    def my_node_info(self, sub_packet: dict):
        print(".../dispatchNodes MyNodeInfo")

    def my_info(self, sub_packet: dict):
        data, conn_id, timestamp, meta = (
            sub_packet["data"],
            sub_packet["connId"],
            sub_packet.get("timestamp"),
            sub_packet["meta"],
        )
        my_info = data["myInfo"]
        print(".../dispatchNodes myInfo")

        self.insert_handlers.insert_my_info ({
            **my_info,
            "connId": conn_id,
            "currentIP": meta["sourceIp"],
            "timestamp": timestamp or meta["timestamp"],
        })

    def node_filter(self, sub_packet: dict):
        data, meta = sub_packet["data"], sub_packet["meta"]
        print(
            "[dispatchNodes] NodeFilter",
            sub_packet,
            decode_node_info(data["nodeName"]),
        )

    def node_highlight(self, sub_packet: dict):
        print("[dispatchNodes] NodeHighlight", sub_packet)

    def node_info(self, sub_packet: dict):
        print("[dispatchNodes] NodeInfo", sub_packet)

    def nodeinfo(self, sub_packet: dict):
        data, meta = sub_packet["data"], sub_packet["meta"]
        num = data["num"]
        # TODO: shape nodeInfo, user, metrics, position
        print("[dispatchNodes] nodeInfo detailed")

    def position(self, sub_packet: dict):
        data, meta = sub_packet["data"], sub_packet["meta"]
        pos = data["position"]

        self.insert_handlers.insert_position ({
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

    def waypoint(self, sub_packet: dict):
        print("[dispatchNodes] Waypoint", sub_packet)

    def user(self, sub_packet: dict):
        print("[dispatchNodes] User", sub_packet)

    def position_debug(self, packet: dict):
        # was handle_Position
        print("[dispatchNodes] Position", packet)
