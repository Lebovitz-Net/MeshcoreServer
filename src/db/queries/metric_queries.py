from src.db.database import db

def _list_telemetry_for_node(num: int):
    return db.execute("""
        SELECT telemetry_id, metric, value, timestamp
        FROM telemetry
        WHERE num = ?
        ORDER BY timestamp DESC
    """, (num,)).fetchall()

def _list_events_for_node(num: int, event_type: str = None):
    if event_type:
        return db.execute("""
            SELECT event_id, event_type, details, timestamp
            FROM event_emissions
            WHERE num = ? AND event_type = ?
            ORDER BY timestamp DESC
        """, (num, event_type)).fetchall()
    else:
        return db.execute("""
            SELECT event_id, event_type, details, timestamp
            FROM event_emissions
            WHERE num = ?
            ORDER BY timestamp DESC
        """, (num,)).fetchall()

def _get_voltage_stats():
    return db.execute("""
        SELECT COUNT(*) AS count,
               AVG(voltage) AS avg_voltage,
               MIN(voltage) AS min_voltage,
               MAX(voltage) AS max_voltage
        FROM device_metrics
        WHERE voltage IS NOT NULL
    """).fetchone()

metric_queries = {
    "list_telemetry_for_node": _list_telemetry_for_node,
    "list_events_for_node": _list_events_for_node,
    "get_voltage_stats": _get_voltage_stats,
}
