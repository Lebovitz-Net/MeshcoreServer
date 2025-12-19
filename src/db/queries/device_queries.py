# src/db/queries/device_queries.py

import json

class DeviceQueries:
    """
    Provides device-related query handlers.
    Expects `self.db` to be a valid database connection.
    """

    def list_devices(self):
        return self.db.execute(
            "SELECT * FROM devices ORDER BY last_seen DESC"
        ).fetchall()

    def get_device(self, device_id):
        return self.db.execute(
            "SELECT * FROM devices WHERE device_id = ?",
            (device_id,),
        ).fetchone()

    def list_device_settings(self, device_id):
        rows = self.db.execute(
            """
            SELECT config_type, config_json, updated_at, conn_id
            FROM device_settings
            WHERE device_id = ?
            ORDER BY config_type ASC
            """,
            (device_id,),
        ).fetchall()

        settings = {}
        for row in rows:
            try:
                settings[row["config_type"]] = json.loads(row["config_json"])
            except Exception:
                settings[row["config_type"]] = None

        return settings

    def get_device_setting(self, device_id, config_type):
        row = self.db.execute(
            """
            SELECT config_type, config_json, updated_at, conn_id
            FROM device_settings
            WHERE device_id = ? AND config_type = ?
            """,
            (device_id, config_type),
        ).fetchone()

        if not row:
            return None

        try:
            config_json = json.loads(row["config_json"])
        except Exception:
            config_json = None

        return {
            "config_type": row["config_type"],
            "config_json": config_json,
            "updated_at": row["updated_at"],
            "conn_id": row["conn_id"],
        }
