# src/db/queries/message_queries.py

class MessageQueries:
    """
    Provides message-related query handlers.
    Expects `self.db` to be a valid database connection.
    """

    def list_messages_for_channel(self, channel_id: int, limit: int = 100):
        return self.db.execute(
            """
            SELECT messageId, channelId, fromNodeNum, toNodeNum,
                   message, recvTimestamp, sentTimestamp,
                   protocol, sender, mentions, options
            FROM messages
            WHERE channelId = ?
            ORDER BY sentTimestamp DESC
            LIMIT ?
            """,
            (channel_id, limit),
        ).fetchall()

    def list_messages(self, channel_id: int = None, since_date: int = 0, limit: int = 500):
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

        return self.db.execute(sql, tuple(params)).fetchall()
