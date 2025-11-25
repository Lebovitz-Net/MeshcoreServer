# src/meshtastic/utils/config_inserts.py

from src.meshtastic.utils.database import db


def _insert_config(sub_packet: dict) -> None:
    """
    Insert a config record into the database.
    """
    sql = """
        INSERT INTO config (
            num, type, payload, timestamp, device_id, conn_id
        ) VALUES (?, ?, ?, ?, ?, ?)
    """
    try:
        cursor = db.cursor()
        cursor.execute(
            sql,
            (
                sub_packet.get("fromNodeNum"),
                sub_packet.get("key"),
                sub_packet.get("data"),
                sub_packet.get("timestamp"),
                sub_packet.get("device_id"),
                sub_packet.get("connId"),
            ),
        )
        db.commit()
    except Exception as err:
        print(f"[DB] Error inserting config: {err}")


def _insert_module_config(sub_packet: dict) -> None:
    """
    Insert a module_config record into the database.
    """
    sql = """
        INSERT INTO module_config (
            num, type, payload, timestamp, device_id, conn_id
        ) VALUES (?, ?, ?, ?, ?, ?)
    """
    try:
        cursor = db.cursor()
        cursor.execute(
            sql,
            (
                sub_packet.get("fromNodeNum"),
                sub_packet.get("key"),
                sub_packet.get("data"),
                sub_packet.get("timestamp"),
                sub_packet.get("device_id"),
                sub_packet.get("connId"),
            ),
        )
        db.commit()
    except Exception as err:
        print(f"[DB] Error inserting module_config: {err}")


def _insert_connection(connection: dict) -> None:
    """
    Insert a connection record into the database.
    """
    sql = """
        INSERT INTO connections (connection_id, num, transport, status)
        VALUES (?, ?, ?, ?)
    """
    try:
        cursor = db.cursor()
        cursor.execute(
            sql,
            (
                connection.get("connection_id"),
                connection.get("num"),
                connection.get("transport"),
                connection.get("status"),
            ),
        )
        db.commit()
    except Exception as err:
        print(f"[DB] Error inserting connection: {err}")


def _insert_file_info(data: dict) -> None:
    """
    Insert a file_info record into the database.
    """
    filename = data.get("filename")
    size = data.get("size")
    from_node_num = data.get("fromNodeNum")

    if not filename or not size or not from_node_num:
        print(
            "[insertFileInfo] Skipped insert: missing required fields",
            filename,
            size,
            from_node_num,
        )
        return

    sql = """
        INSERT INTO file_info (
            filename, size, mime_type, description,
            num, timestamp, conn_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    try:
        cursor = db.cursor()
        cursor.execute(
            sql,
            (
                filename,
                size,
                data.get("mime_type"),
                data.get("description"),
                from_node_num,
                data.get("timestamp"),
                data.get("connId"),
            ),
        )
        db.commit()
    except Exception as err:
        print(f"[DB] Error inserting file_info: {err}")


def _insert_metadata(sub_packet: dict) -> None:
    """
    Insert a metadata record into the database.
    """
    sql = """
        INSERT INTO metadata (
            num, firmwareVersion, deviceStateVersion, canShutdown,
            hasWifi, hasBluetooth, hwModel, hasPKC, excludedModules
        ) VALUES (
            :num, :firmwareVersion, :deviceStateVersion, :canShutdown,
            :hasWifi, :hasBluetooth, :hwModel, :hasPKC, :excludedModules
        )
    """
    try:
        cursor = db.cursor()
        cursor.execute(sql, sub_packet)
        db.commit()
    except Exception as err:
        print(f"[DB] Error inserting metadata: {err}")


# Exported object of insert functions
config_inserts = {
    "insert_config": _insert_config,
    "insert_module_config": _insert_module_config,
    "insert_connection": _insert_connection,
    "insert_file_info": _insert_file_info,
    "insert_metadata": _insert_metadata,
}
