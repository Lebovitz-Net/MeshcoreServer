# src/meshtastic/utils/contact_inserts.py

from src.meshtastic.utils.database import db


def _insert_users(user: dict) -> None:
    """
    Insert or update a user record in the database.
    """
    sql = """
        INSERT INTO users (
            contactId, type, name, publicKey, timestamp, protocol, connId,
            nodeNum, shortName,         -- Meshtastic
            times, options, position    -- Protocol Specific
        ) VALUES (
            :contactId, :type, :name, :publicKey, :timestamp, :protocol, :connId,
            :nodeNum, :shortName,
            :times, :options, :position
        )
        ON CONFLICT(contactId) DO UPDATE SET
            name = excluded.name,
            shortName = excluded.shortName,
            publicKey = excluded.publicKey
    """

    try:
        cursor = db.cursor()
        cursor.execute(sql, user)
        db.commit()
    except Exception as err:
        print(f"[DB] Error inserting user: {err}")


# Exported object of insert functions
contact_inserts = {
    "insert_users": _insert_users,
}
