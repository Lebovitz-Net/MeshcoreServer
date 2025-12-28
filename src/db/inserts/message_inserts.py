# src/db/inserts/message_inserts.py

import time
from src.utils import normalize_in

class MessageInserts:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    """
    Provides the insert_message handler.
    Expects `self.db` to be a valid database connection.
    """

    def insert_message(self, msg: dict) -> None:
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
        self.sse_emitter.emit("message_arrived", {
            **msg,
            "timestamp": msg.get("timestamp", int(time.time() * 1000)),
        })
        try:
            cursor = self.db.cursor()
            cursor.execute(
                sql,
                {
                    **msg,
                    "recvTimestamp": recv_timestamp,
                    "sentTimestamp": sent_timestamp,
                },
            )
            self.db.commit()
        except Exception as err:
            print(f"[DB] Error inserting message: {err}")
            return

