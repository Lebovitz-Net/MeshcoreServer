# src/db/inserts/config_inserts.py

class ConfigInserts:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    """
    Provides config-related insert handlers.
    Expects `self.db` to be a valid database connection.
    """

    def insert_config(self, sub_packet: dict) -> None:
        sql = """
            INSERT INTO config (
                num, type, payload, timestamp, device_id, conn_id
            ) VALUES (?, ?, ?, ?, ?, ?)
        """
        try:
            cursor = self.db.cursor()
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
            self.db.commit()
        except Exception as err:
            print(f"[DB] Error inserting config: {err}")

    def insert_module_config(self, sub_packet: dict) -> None:
        sql = """
            INSERT INTO module_config (
                num, type, payload, timestamp, device_id, conn_id
            ) VALUES (?, ?, ?, ?, ?, ?)
        """
        try:
            cursor = self.db.cursor()
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
            self.db.commit()
        except Exception as err:
            print(f"[DB] Error inserting module_config: {err}")

    def insert_connection(self, connection: dict) -> None:
        sql = """
            INSERT INTO connections (connection_id, num, transport, status)
            VALUES (?, ?, ?, ?)
        """
        try:
            cursor = self.db.cursor()
            cursor.execute(
                sql,
                (
                    connection.get("connection_id"),
                    connection.get("num"),
                    connection.get("transport"),
                    connection.get("status"),
                ),
            )
            self.db.commit()
        except Exception as err:
            print(f"[DB] Error inserting connection: {err}")

    def insert_file_info(self, data: dict) -> None:
        filename = data.get("filename")
        size = data.get("size")
        from_node_num = data.get("fromNodeNum")

        if not filename or not size or not from_node_num:
            print("[insertFileInfo] Skipped insert: missing required fields", filename, size, from_node_num)
            return

        sql = """
            INSERT INTO file_info (
                filename, size, mime_type, description,
                num, timestamp, conn_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        try:
            cursor = self.db.cursor()
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
            self.db.commit()
        except Exception as err:
            print(f"[DB] Error inserting file_info: {err}")

    def insert_metadata(self, sub_packet: dict) -> None:
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
            cursor = self.db.cursor()
            cursor.execute(sql, sub_packet)
            self.db.commit()
        except Exception as err:
            print(f"[DB] Error inserting metadata: {err}")
