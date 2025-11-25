# src/meshtastic/utils/diagnostic_inserts.py

import json
import time
from src.meshtastic.utils.database import db, db_boolean


def _insert_log_record(data: dict) -> None:
    message = data.get("message")
    from_node_num = data.get("fromNodeNum")
    timestamp = data.get("timestamp")
    conn_id = data.get("connId")

    if not message or not isinstance(from_node_num, (int, float)):
        print("[insertLogRecord] Skipped insert: missing required fields", data)
        return

    sql = """
        INSERT OR IGNORE INTO log_records (
          num, packetType, message, timestamp, connId, decodeStatus
        ) VALUES (?, ?, ?, ?, ?, ?)
    """
    try:
        cursor = db.cursor()
        cursor.execute(sql, (from_node_num, "logRecord", message, timestamp, conn_id, db_boolean(True)))
        db.commit()
    except Exception as err:
        print(f"[DB] Error inserting log_record: {err}")


def _insert_packet_log(packet: dict) -> bool:
    num = packet.get("num")
    packet_type = packet.get("packet_type")
    timestamp = packet.get("timestamp")
    raw_payload = packet.get("raw_payload")

    if not num:
        print("[insertPacketLog] Skipping log: no num provided")
        return False

    try:
        cursor = db.cursor()
        cursor.execute("SELECT 1 FROM nodes WHERE num = ?", (num,))
        exists = cursor.fetchone()
        if not exists:
            print(f"[insertPacketLog] Skipping log: no parent node for num={num}")
            return False

        sql = """
            INSERT INTO packet_logs (
              num, packet_type, timestamp, raw_payload
            ) VALUES (?, ?, ?, ?)
        """
        cursor.execute(sql, (num, packet_type, timestamp, raw_payload))
        db.commit()
        return True
    except Exception as err:
        print(f"[DB] Error inserting packet_log: {err}")
        return False


def _inject_packet_log(packet: dict) -> dict:
    num = packet.get("num")
    packet_type = packet.get("packet_type")
    raw_payload = packet.get("raw_payload")
    timestamp = packet.get("timestamp", int(time.time()))

    if not num or not packet_type or raw_payload is None:
        raise ValueError("Missing required fields: num, packet_type, raw_payload")

    payload = raw_payload if isinstance(raw_payload, str) else json.dumps(raw_payload)

    sql = """
        INSERT INTO packet_logs (num, packet_type, raw_payload, timestamp)
        VALUES (?, ?, ?, ?)
    """
    try:
        cursor = db.cursor()
        cursor.execute(sql, (num, packet_type, payload, timestamp))
        db.commit()

        cursor.execute("SELECT last_insert_rowid() AS id")
        row = cursor.fetchone()
        return {"inserted": True, "log_id": row["id"] if row else None}
    except Exception as err:
        print(f"[DB] Error injecting packet_log: {err}")
        return {"inserted": False, "log_id": None}


def _insert_trace_data(trace: dict) -> None:
    data = trace.get("data", {})
    meta = trace.get("meta", {})

    inner = data.get("data", {})
    tag = inner.get("tag")
    path_len = inner.get("pathLen")
    last_snr = inner.get("lastSnr")
    path_hashes = inner.get("pathHashes", [])
    path_snrs = inner.get("pathSnrs", [])

    conn_id = meta.get("connId")
    timestamp = meta.get("timestamp")

    payload_hashes = json.dumps(path_hashes)
    payload_snrs = json.dumps(path_snrs)

    sql = """
        INSERT INTO trace_logs (
          connId, nodeNum, tag, pathLen, lastSnr,
          pathHashes, pathSnrs, timestamp
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    try:
        cursor = db.cursor()
        cursor.execute(sql, (conn_id, None, tag, path_len, last_snr, payload_hashes, payload_snrs, timestamp))
        db.commit()
    except Exception as err:
        print(f"[DB] Error inserting trace_data: {err}")


def _insert_diagnostic_overlay(overlay: dict) -> None:
    raise NotImplementedError("insertDiagnosticOverlay not yet implemented")


def _insert_overlay_preview(preview: dict) -> None:
    raise NotImplementedError("insertOverlayPreview not yet implemented")


def _insert_config_mutation(mutation: dict) -> None:
    raise NotImplementedError("insertConfigMutation not yet implemented")


# Exported object of insert functions
diagnostic_inserts = {
    "insert_log_record": _insert_log_record,
    "insert_packet_log": _insert_packet_log,
    "inject_packet_log": _inject_packet_log,
    "insert_trace_data": _insert_trace_data,
    "insert_diagnostic_overlay": _insert_diagnostic_overlay,
    "insert_overlay_preview": _insert_overlay_preview,
    "insert_config_mutation": _insert_config_mutation,
}
