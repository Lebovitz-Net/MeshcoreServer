# src/db/queries/diagnostic_queries.py

class DiagnosticQueries:
    """
    Provides diagnostic/log query handlers.
    Expects `self.db` to be a valid database connection.
    """

    def list_logs(self, limit: int = 200):
        return self.db.execute(
            """
            SELECT log_id, num, packet_type, raw_payload, timestamp
            FROM packet_logs
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    def list_packet_logs(self, limit: int = 100):
        return self.db.execute(
            """
            SELECT log_id, num, packet_type, raw_payload, timestamp
            FROM packet_logs
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    def get_packet_log(self, log_id: int):
        return self.db.execute(
            """
            SELECT log_id, num, packet_type, raw_payload, timestamp
            FROM packet_logs
            WHERE log_id = ?
            """,
            (log_id,),
        ).fetchone()

    def list_recent_packet_logs_for_node(self, num: int, limit: int = 100):
        return self.db.execute(
            """
            SELECT log_id, packet_type, timestamp, raw_payload
            FROM packet_logs
            WHERE num = ?
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (num, limit),
        ).fetchall()
