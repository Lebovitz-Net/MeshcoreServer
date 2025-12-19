# src/db/queries/metric_queries.py

class MetricQueries:
    """
    Provides telemetry and metrics query handlers.
    Expects `self.db` to be a valid database connection.
    """

    def list_telemetry_for_node(self, num: int):
        return self.db.execute(
            """
            SELECT telemetry_id, metric, value, timestamp
            FROM telemetry
            WHERE num = ?
            ORDER BY timestamp DESC
            """,
            (num,),
        ).fetchall()

    def list_events_for_node(self, num: int, event_type: str = None):
        if event_type:
            return self.db.execute(
                """
                SELECT event_id, event_type, details, timestamp
                FROM event_emissions
                WHERE num = ? AND event_type = ?
                ORDER BY timestamp DESC
                """,
                (num, event_type),
            ).fetchall()

        return self.db.execute(
            """
            SELECT event_id, event_type, details, timestamp
            FROM event_emissions
            WHERE num = ?
            ORDER BY timestamp DESC
            """,
            (num,),
        ).fetchall()

    def get_voltage_stats(self):
        return self.db.execute(
            """
            SELECT COUNT(*) AS count,
                   AVG(voltage) AS avg_voltage,
                   MIN(voltage) AS min_voltage,
                   MAX(voltage) AS max_voltage
            FROM device_metrics
            WHERE voltage IS NOT NULL
            """
        ).fetchone()
