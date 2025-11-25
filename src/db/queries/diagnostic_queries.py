from src.db.database import db

def _list_logs(limit: int = 200):
    return db.execute("""
        SELECT log_id, num, packet_type, raw_payload, timestamp
        FROM packet_logs
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,)).fetchall()

def _list_packet_logs(limit: int = 100):
    return db.execute("""
        SELECT log_id, num, packet_type, raw_payload, timestamp
        FROM packet_logs
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,)).fetchall()

def _get_packet_log(log_id: int):
    return db.execute("""
        SELECT log_id, num, packet_type, raw_payload, timestamp
        FROM packet_logs
        WHERE log_id = ?
    """, (log_id,)).fetchone()

def _list_recent_packet_logs_for_node(num: int, limit: int = 100):
    return db.execute("""
        SELECT log_id, packet_type, timestamp, raw_payload
        FROM packet_logs
        WHERE num = ?
        ORDER BY timestamp DESC
        LIMIT ?
    """, (num, limit)).fetchall()

diagnostic_queries = {
    "list_logs": _list_logs,
    "list_packet_logs": _list_packet_logs,
    "get_packet_log": _get_packet_log,
    "list_recent_packet_logs_for_node": _list_recent_packet_logs_for_node,
}
