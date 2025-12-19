# src/db/inserts/contact_inserts.py

class ContactInserts:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    """
    Provides user/contact insert handlers.
    """

    def insert_users(self, user: dict) -> None:
        sql = """
            INSERT INTO users (
                contactId, type, name, publicKey, timestamp, protocol, connId,
                nodeNum, shortName, times, options, position
            ) VALUES (
                :contactId, :type, :name, :publicKey, :timestamp, :protocol, :connId,
                :nodeNum, :shortName, :times, :options, :position
            )
            ON CONFLICT(contactId) DO UPDATE SET
                name = excluded.name,
                shortName = excluded.shortName,
                publicKey = excluded.publicKey
        """
        try:
            cursor = self.db.cursor()
            cursor.execute(sql, user)
            self.db.commit()
        except Exception as err:
            print(f"[DB] Error inserting user: {err}")
