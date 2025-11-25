from src.db.database import db

def _get_full_config():
    return {
        "protocolMap": db.execute("SELECT * FROM protocol_map ORDER BY portnum").fetchall(),
        "deviceSettings": db.execute("SELECT * FROM device_settings ORDER BY num").fetchall(),
        "deviceMeta": db.execute("SELECT * FROM device_meta ORDER BY num").fetchall(),
        "overlays": db.execute("SELECT * FROM diagnostic_overlay ORDER BY overlay_id").fetchall(),
        "queueStatus": db.execute("""
            SELECT qs.* FROM queue_status qs
            JOIN (
              SELECT num, MAX(timestamp) AS latest
              FROM queue_status
              GROUP BY num
            ) latest_qs ON qs.num = latest_qs.num AND qs.timestamp = latest_qs.latest
            ORDER BY qs.num
        """).fetchall(),
    }

def _get_config(config_id):
    return db.execute("SELECT config_id, config_json, updated_at FROM config WHERE config_id = ?", (config_id,)).fetchone()

def _list_all_configs():
    return db.execute("SELECT config_id, config_json, updated_at FROM config ORDER BY updated_at DESC").fetchall()

def _get_module_config(module_id):
    return db.execute("SELECT module_id, config_json, updated_at FROM module_config WHERE module_id = ?", (module_id,)).fetchone()

def _list_all_module_configs():
    return db.execute("SELECT module_id, config_json, updated_at FROM module_config ORDER BY updated_at DESC").fetchall()

def _get_metadata_by_key(key):
    return db.execute("SELECT meta_id, key, value, updated_at FROM metadata WHERE key = ?", (key,)).fetchone()

def _list_all_metadata():
    return db.execute("SELECT meta_id, key, value, updated_at FROM metadata ORDER BY updated_at DESC").fetchall()

def _list_file_info():
    return db.execute("SELECT file_id, filename, size, uploaded_at FROM file_info ORDER BY uploaded_at DESC").fetchall()

config_queries = {
    "get_full_config": _get_full_config,
    "get_config": _get_config,
    "list_all_configs": _list_all_configs,
    "get_module_config": _get_module_config,
    "list_all_module_configs": _list_all_module_configs,
    "get_metadata_by_key": _get_metadata_by_key,
    "list_all_metadata": _list_all_metadata,
    "list_file_info": _list_file_info,
}
