import json
from src.db.database import db

def _list_devices():
    return db.execute("SELECT * FROM devices ORDER BY last_seen DESC").fetchall()

def _get_device(device_id):
    return db.execute("SELECT * FROM devices WHERE device_id = ?", (device_id,)).fetchone()

def _list_device_settings(device_id):
    rows = db.execute("""
        SELECT config_type, config_json, updated_at, conn_id
        FROM device_settings
        WHERE device_id = ?
        ORDER BY config_type ASC
    """, (device_id,)).fetchall()

    settings = {}
    for row in rows:
        try:
            settings[row["config_type"]] = json.loads(row["config_json"])
        except Exception:
            settings[row["config_type"]] = None
    return settings

def _get_device_setting(device_id, config_type):
    row = db.execute("""
        SELECT config_type, config_json, updated_at, conn_id
        FROM device_settings
        WHERE device_id = ? AND config_type = ?
    """, (device_id, config_type)).fetchone()

    if not row:
        return None
    try:
        return {
            "config_type": row["config_type"],
            "config_json": json.loads(row["config_json"]),
            "updated_at": row["updated_at"],
            "conn_id": row["conn_id"],
        }
    except Exception:
        return {
            "config_type": row["config_type"],
            "config_json": None,
            "updated_at": row["updated_at"],
            "conn_id": row["conn_id"],
        }

device_queries = {
    "list_devices": _list_devices,
    "get_device": _get_device,
    "list_device_settings": _list_device_settings,
    "get_device_setting": _get_device_setting,
}
