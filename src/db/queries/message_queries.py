from src.db.database import db

def _list_messages_for_channel(channel_id: int, limit: int = 100):
    return db.execute("""
        SELECT messageId, channelId, fromNodeNum, toNodeNum,
               message, recvTimestamp, sentTimestamp,
               protocol, sender, mentions, options
        FROM messages
        WHERE channelId = ?
        ORDER BY sentTimestamp DESC
        LIMIT ?
    """, (channel_id, limit)).fetchall()

def _list_messages(channel_id: int = None, since_date: int = 0, limit: int = 500):
    sql = """
        SELECT messageId, channelId, fromNodeNum, toNodeNum,
               message, recvTimestamp, sentTimestamp,
               protocol, sender, mentions, options
        FROM messages
        WHERE 1=1
    """
    params = []
    if channel_id is not None:
        sql += " AND channelId = ?"
        params.append(channel_id)
    if since_date > 0:
        sql += " AND recvTimestamp > ?"
        params.append(since_date)
    sql += " ORDER BY recvTimestamp DESC LIMIT ?"
    params.append(limit)

    return db.execute(sql, tuple(params)).fetchall()

message_queries = {
    "list_messages_for_channel": _list_messages_for_channel,
    "list_messages": _list_messages,
}
