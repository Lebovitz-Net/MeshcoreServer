# src/meshtastic/utils/channel_inserts.py

import time
from src.meshtastic.utils.database import db
from src.servers.sse_emitters import emit_channel_update


def _insert_channel(packet: dict) -> None:
    """
    Insert or replace a channel record in the database,
    then emit a channel update event.
    """
    sql = """
        INSERT OR REPLACE INTO channels (
            channelIdx,
            channelNum,
            nodeNum,
            protocol,
            name,
            role,
            psk,
            options,
            timestamp,
            connId
        ) VALUES (
            :channelIdx,
            :channelNum,
            :nodeNum,
            :protocol,
            :name,
            :role,
            :psk,
            :options,
            :timestamp,
            :connId
        )
    """

    try:
        cursor = db.cursor()
        cursor.execute(sql, packet)
        db.commit()
    except Exception as err:
        print(f"[DB] Error inserting channel: {err}")
        return

    # Emit channel update with updatedAt timestamp
    emit_channel_update({
        **packet,
        "updatedAt": int(time.time() * 1000),  # ms timestamp
    })


# Exported object of insert functions
channel_inserts = {
    "insert_channel": _insert_channel,
}
