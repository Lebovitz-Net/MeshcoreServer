# src/db/inserts/channel_inserts.py

import time

class ChannelInserts:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    """
    Provides the insert_channel handler.
    Expects `self.db` to be a valid database connection.
    """

    def insert_channel(self, packet: dict) -> None:
        sql = """
            INSERT OR REPLACE INTO channels (
                channelIdx, channelNum, nodeNum, protocol, name,
                role, psk, options, timestamp, connId
            ) VALUES (
                :channelIdx, :channelNum, :nodeNum, :protocol, :name,
                :role, :psk, :options, :timestamp, :connId
            )
        """

        try:
            cursor = self.db.cursor()
            cursor.execute(sql, packet)
            self.db.commit()
        except Exception as err:
            print(f"[DB] Error inserting channel: {err}")
            return
        print (".../CHANNEL INSERT SSE EMITTER", type(self.sse_emitter))
        self.sse_emitter.emit("channel_updated", {
            **packet,
            "updatedAt": int(time.time() * 1000),
        })
