# src/db/inserts/node_inserts.py

import json
import time
from src.meshtastic.node_mapping import set_mapping, set_channel_mapping


class NodeInserts:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    """
    Provides node-related insert handlers.
    Expects `self.db` to be a valid database connection.
    """

    def insert_node(self, node: dict, timestamp: int = None) -> None:
        if not node or not node.get("num"):
            print("[insertNode] Skipping insert: node.num is missing")
            return

        ts = timestamp or int(time.time() * 1000)

        sql = """
            INSERT INTO nodes (num, label, last_seen, viaMqtt, hopsAway, lastHeard, device_id)
            VALUES (:num, :label, :last_seen, :viaMqtt, :hopsAway, :lastHeard, :device_id)
            ON CONFLICT(num) DO UPDATE SET
              label = excluded.label,
              last_seen = excluded.last_seen,
              viaMqtt = excluded.viaMqtt,
              hopsAway = excluded.hopsAway,
              lastHeard = excluded.lastHeard,
              device_id = excluded.device_id
        """

        try:
            cursor = self.db.cursor()
            cursor.execute(
                sql,
                {
                    "num": node.get("num"),
                    "label": node.get("label"),
                    "last_seen": node.get("last_seen") or ts,
                    "viaMqtt": 1 if node.get("viaMqtt") else 0,
                    "hopsAway": node.get("hopsAway"),
                    "lastHeard": node.get("lastHeard"),
                    "device_id": node.get("device_id"),
                },
            )
            self.db.commit()
        except Exception as err:
            print(f"[DB] Error inserting node: {err}")

    def insert_node_metrics(self, device_metrics: dict, meta: dict) -> None:
        num = meta.get("num")
        last_heard = meta.get("lastHeard", int(time.time() * 1000))

        sql = """
            INSERT INTO node_metrics (
              nodeNum, lastHeard, metrics, updatedAt
            ) VALUES (
              :nodeNum, :lastHeard, :metrics, :updatedAt
            )
            ON CONFLICT(nodeNum) DO UPDATE SET
              lastHeard = excluded.lastHeard,
              metrics = excluded.metrics,
              updatedAt = excluded.updatedAt
        """

        try:
            cursor = self.db.cursor()
            cursor.execute(
                sql,
                {
                    "nodeNum": num,
                    "lastHeard": last_heard,
                    "metrics": json.dumps(device_metrics),
                    "updatedAt": int(time.time() * 1000),
                },
            )
            self.db.commit()
        except Exception as err:
            print(f"[DB] Error inserting node_metrics: {err}")

    def insert_position(self, decoded: dict) -> None:
        from_node_num = decoded.get("fromNodeNum")
        to_node_num = decoded.get("toNodeNum")
        latitude = decoded.get("latitude")
        longitude = decoded.get("longitude")
        altitude = decoded.get("altitude")
        ts = decoded.get("timestamp") or int(time.time() * 1000)

        sql = """
            INSERT INTO positions (fromNodeNum, toNodeNum, latitude, longitude, altitude, timestamp)
            VALUES (:fromNodeNum, :toNodeNum, :latitude, :longitude, :altitude, :ts)
        """

        try:
            cursor = self.db.cursor()
            cursor.execute(
                sql,
                {
                    "fromNodeNum": from_node_num,
                    "toNodeNum": to_node_num,
                    "latitude": float(latitude) if latitude is not None else None,
                    "longitude": float(longitude) if longitude is not None else None,
                    "altitude": float(altitude) if altitude is not None else None,
                    "ts": ts,
                },
            )
            self.db.commit()
        except Exception as err:
            print(f"[DB] Error inserting position: {err}")

    def upsert_node_info(self, packet: dict) -> dict | None:
        node_info = packet.get("nodeInfo", {})
        user = packet.get("user", {})
        position = packet.get("position")
        device_metrics = packet.get("deviceMetrics")
        num = node_info.get("num")

        if not num:
            print("[upsertNodeInfo] Skipping: nodeInfo.num is missing", node_info)
            return None

        try:
            # Insert or update the node itself
            self.insert_node(node_info)

            # Insert user info if present
            if user.get("id"):
                # Calls ContactInsert.insert_users via mixin
                self.insert_users(user)

            # Insert node metrics if present
            if device_metrics is not None:
                self.insert_node_metrics(device_metrics, {"num": num})

            # Insert position if present
            if position:
                self.insert_position(position)

            # Emit update
            self.sse_emitter.emit("node_updated", node_info)

            return {"num": num}

        except Exception as err:
            print(f"[DB] Error upserting node_info: {err}")
            return None

    def insert_my_info(self, packet: dict) -> None:
        my_node_num = packet.get("myNodeNum")
        current_ip = packet.get("currentIP")
        channel = packet.get("channel")

        if not my_node_num or not current_ip:
            print("[insertMyInfo] Missing required fields:", {"myNodeNum": my_node_num, "currentIP": current_ip}, packet)
            return

        set_mapping(current_ip, my_node_num, current_ip)
        set_channel_mapping(channel or 0, my_node_num)

        sql = """
            INSERT INTO my_info (
            myNodeNum, name, type, options, publicKey, protocol,
            currentIP, connId, timestamp
            ) VALUES (
            :myNodeNum, :name, :type, :options, :publicKey, :protocol,
            :currentIP, :connId, :timestamp
            )
            ON CONFLICT(myNodeNum) DO UPDATE SET
            publicKey = excluded.publicKey,
            currentIP = excluded.currentIP,
            connId = excluded.connId,
            timestamp = excluded.timestamp
        """
        try:
            cursor = self.db.cursor()
            cursor.execute(sql, packet)
            self.db.commit()
        except Exception as err:
            print(f"[insertMyInfo] DB insert failed: {err}")
