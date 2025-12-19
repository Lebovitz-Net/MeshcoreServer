# src/db/queries/config_queries.py

class ConfigQueries:
    """
    Provides configuration- and metadata-related query handlers.
    Expects `self.db` to be a valid database connection.
    """

    def get_full_config(self):
        return {
            "protocolMap": self.db.execute(
                "SELECT * FROM protocol_map ORDER BY portnum"
            ).fetchall(),

            "deviceSettings": self.db.execute(
                "SELECT * FROM device_settings ORDER BY num"
            ).fetchall(),

            "deviceMeta": self.db.execute(
                "SELECT * FROM device_meta ORDER BY num"
            ).fetchall(),

            "overlays": self.db.execute(
                "SELECT * FROM diagnostic_overlay ORDER BY overlay_id"
            ).fetchall(),

            "queueStatus": self.db.execute(
                """
                SELECT qs.* FROM queue_status qs
                JOIN (
                  SELECT num, MAX(timestamp) AS latest
                  FROM queue_status
                  GROUP BY num
                ) latest_qs
                ON qs.num = latest_qs.num AND qs.timestamp = latest_qs.latest
                ORDER BY qs.num
                """
            ).fetchall(),
        }

    def get_config(self, config_id):
        return self.db.execute(
            "SELECT config_id, config_json, updated_at FROM config WHERE config_id = ?",
            (config_id,),
        ).fetchone()

    def list_all_configs(self):
        return self.db.execute(
            "SELECT config_id, config_json, updated_at FROM config ORDER BY updated_at DESC"
        ).fetchall()

    def get_module_config(self, module_id):
        return self.db.execute(
            "SELECT module_id, config_json, updated_at FROM module_config WHERE module_id = ?",
            (module_id,),
        ).fetchone()

    def list_all_module_configs(self):
        return self.db.execute(
            "SELECT module_id, config_json, updated_at FROM module_config ORDER BY updated_at DESC"
        ).fetchall()

    def get_metadata_by_key(self, key):
        return self.db.execute(
            "SELECT meta_id, key, value, updated_at FROM metadata WHERE key = ?",
            (key,),
        ).fetchone()

    def list_all_metadata(self):
        return self.db.execute(
            "SELECT meta_id, key, value, updated_at FROM metadata ORDER BY updated_at DESC"
        ).fetchall()

    def list_file_info(self):
        return self.db.execute(
            "SELECT file_id, filename, size, uploaded_at FROM file_info ORDER BY uploaded_at DESC"
        ).fetchall()
