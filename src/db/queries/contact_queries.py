# src/db/queries/contact_queries.py

class ContactQueries:
    """
    Provides contact/user query handlers.
    Expects `self.db` to be a valid database connection.
    """

    def list_contacts(self, limit: int = 500):
        return self.db.execute(
            """
            SELECT contactId, type, name, publicKey, timestamp, protocol,
                   nodeNum, shortName, times, options, position, connId
            FROM users
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
