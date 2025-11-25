# src/meshtastic/utils/node_inserts.py

import json
import time
from src.meshtastic.utils.database import db
from src.servers.sse_emitters import emit_node_update
from src.meshtastic.utils.node_mapping import set_mapping, set_channel_mapping
from src.meshtastic.utils.contact_inserts import contact_inserts


def _insert_node(node: dict, timestamp: int = None) -> None:
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
        cursor = db.cursor()
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
        db.commit()
    except Exception as err:
        print(f"[DB] Error inserting node: {err}")


def _insert_node_metrics(device_metrics: dict, meta: dict) -> None:
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
        cursor = db.cursor()
        cursor.execute(
            sql,
            {
                "nodeNum": num,
                "lastHeard": last_heard,
                "metrics": json.dumps(device_metrics),
                "updatedAt": int(time.time() * 1000),
            },
        )
        db.commit()
    except Exception as err:
        print(f"[DB] Error inserting node_metrics: {err}")


def _insert_position(decoded: dict) -> None:
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
        cursor = db.cursor()
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
        db.commit()
    except Exception as err:
        print(f"[DB] Error inserting position: {err}")


def _upsert_node_info(packet: dict) -> dict | None:
    node_info = packet.get("nodeInfo", {})
    user = packet.get("user", {})
    position = packet.get("position")
    device_metrics = packet.get("deviceMetrics")
    num = node_info.get("num")

    if not num:
        print("[upsertNodeInfo] Skipping: nodeInfo.num is missing", node_info)
        return None

    try:
        _insert_node(node_info)

        if user.get("id"):
            contact_inserts["insert_users"](user)

        if device_metrics is not None:
            _insert_node_metrics(device_metrics, {"num": num})

        if position:
            _insert_position(position)

        emit_node_update(node_info)

        return {"num": num}
    except Exception as err:
        print(f"[DB] Error upserting node_info: {err}")
        return None


def _insert_my_info(packet: dict) -> None:
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
        cursor = db.cursor()
        cursor.execute(sql, packet)
        db.commit()
    except Exception as err:
        print(f"[insertMyInfo] DB insert failed: {err}")


# Exported object of insert functions
node_inserts = {
    "insert_node": _insert_node,
    "insert_node_metrics": _insert_node_metrics,
    "insert_position": _insert_position,
    "upsert_node_info": _upsert_node_info,
    "insert_my_info": _insert_my_info,
}
