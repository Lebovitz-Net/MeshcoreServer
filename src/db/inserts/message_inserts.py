# src/meshtastic/utils/message_inserts.py

import time
from src.meshtastic.utils.database import db
from src.servers.sse_emitters import emit_message_update
from src.utils import normalize_in


def _insert_message(msg: dict) -> None:
    """
    Insert a message record into the database and emit a message update.
    """
    recv_timestamp = normalize_in(msg.get("recvTimestamp"))
    sent_timestamp = normalize_in(msg.get("sentTimestamp"))

    sql = """
        INSERT INTO messages (
          contactId, messageId, channelId, fromNodeNum, toNodeNum,
          message, recvTimestamp,
          sentTimestamp, protocol, sender, mentions, options
        )
        VALUES (
          :contactId, :messageId, :channelId, :fromNodeNum, :toNodeNum,
          :message, :recvTimestamp,
          :sentTimestamp, :protocol, :sender, :mentions, :options
        )
    """

    try:
        cursor = db.cursor()
        cursor.execute(
            sql,
            {
                **msg,
                "recvTimestamp": recv_timestamp,
                "sentTimestamp": sent_timestamp,
            },
        )
        db.commit()
    except Exception as err:
        print(f"[DB] Error inserting message: {err}")
        return

    # Emit message update with timestamp fallback
    emit_message_update({
        **msg,
        "timestamp": msg.get("timestamp", int(time.time() * 1000)),
    })


# Exported object of insert functions
message_inserts = {
    "insert_message": _insert_message,
}
