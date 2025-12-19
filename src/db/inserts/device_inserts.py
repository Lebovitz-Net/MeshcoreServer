# src/db/inserts/device_inserts.py

class DeviceInserts:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    """
    Provides device-related insert handlers.
    """

    def insert_device(self, device: dict) -> None:
        if not device.get("device_id"):
            print("[insertDevice] Skipped insert: missing device_id")
            return

        sql = """
            INSERT INTO devices (device_id, num, conn_id, device_type, last_seen)
            VALUES (?, ?, ?, ?, strftime('%s','now'))
            ON CONFLICT(device_id) DO UPDATE SET
              num = excluded.num,
              conn_id = excluded.conn_id,
              device_type = excluded.device_type,
              last_seen = strftime('%s','now')
        """
        try:
            cursor = self.db.cursor()
            cursor.execute(
                sql,
                (
                    device.get("device_id"),
                    device.get("num"),
                    device.get("conn_id"),
                    device.get("device_type", "meshtastic"),
                ),
            )
            self.db.commit()
        except Exception as err:
            print(f"[DB] Error inserting device: {err}")

    def insert_device_setting(self, setting: dict) -> None:
        if not setting.get("device_id") or not setting.get("config_type") or not setting.get("config_json"):
            print("[insertDeviceSetting] Skipped insert: missing required fields", setting)
            return

        sql = """
            INSERT INTO device_settings (device_id, config_type, config_json, conn_id, updated_at)
            VALUES (?, ?, ?, ?, strftime('%s','now'))
            ON CONFLICT(device_id, config_type) DO UPDATE SET
              num         = excluded.num,
              config_json = excluded.config_json,
              conn_id     = excluded.conn_id,
              updated_at  = excluded.updated_at
        """
        try:
            cursor = self.db.cursor()
            cursor.execute(
                sql,
                (
                    setting.get("device_id"),
                    setting.get("config_type"),
                    setting.get("config_json"),
                    setting.get("conn_id"),
                ),
            )
            self.db.commit()
        except Exception as err:
            print(f"[DB] Error inserting device_setting: {err}")

    def insert_device_meta(self, meta: dict) -> None:
        if not meta.get("device_id"):
            print("[insertDeviceMeta] Skipped insert: missing device_id")
            return

        sql = """
            INSERT INTO device_meta (
              device_id, reboot_count, min_app_version, pio_env,
              firmware_version, hw_model, conn_id, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, strftime('%s','now'))
        """
        try:
            cursor = self.db.cursor()
            cursor.execute(
                sql,
                (
                    meta.get("device_id"),
                    meta.get("reboot_count"),
                    meta.get("min_app_version"),
                    meta.get("pio_env"),
                    meta.get("firmware_version"),
                    meta.get("hw_model"),
                    meta.get("conn_id"),
                ),
            )
            self.db.commit()
        except Exception as err:
            print(f"[DB] Error inserting device_meta: {err}")

    def upsert_device_ip_map(self, mapping: dict) -> None:
        sql = """
            INSERT INTO device_ip_map (source_ip, num, device_id, last_seen)
            VALUES (:source_ip, :num, :device_id, :last_seen)
            ON CONFLICT(source_ip) DO UPDATE SET
              num = excluded.num,
              device_id = excluded.device_id,
              last_seen = excluded.last_seen
        """
        try:
            cursor = self.db.cursor()
            cursor.execute(sql, mapping)
            self.db.commit()
        except Exception as err:
            print(f"[DB] Error upserting device_ip_map: {err}")

    def lookup_device_ip_map(self, source_ip: str) -> dict | None:
        sql = """
            SELECT num, device_id
            FROM device_ip_map
            WHERE source_ip = ?
        """
        try:
            cursor = self.db.cursor()
            cursor.execute(sql, (source_ip,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as err:
            print(f"[DB] Error looking up device_ip_map: {err}")
            return None
