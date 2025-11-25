from src.db.database import db

def _list_contacts(limit: int = 500):
    return db.execute("""
        SELECT contactId, type, name, publicKey, timestamp, protocol,
               nodeNum, shortName, times, options, position, connId
        FROM users
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,)).fetchall()

contact_queries = {
    "list_contacts": _list_contacts,
}
