dbMessages = [
    
    """
    CREATE TABLE IF NOT EXISTS messages (
      -- Core
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      contactId TEXT NOT NULL,
      channelId INTEGER NOT NULL,
      message TEXT NOT NULL,

      -- Meshcore Specific 
      sender TEXT,                         -- e.g. "Nick D"
      mentions TEXT,              -- JSON array: '["KD1MU", "W1AW"]'

      -- Meshtastic-specific
      fromNodeNum INTEGER,
      toNodeNum INTEGER,
      toNodeType INTEGER DEFAULT 0,
      messageId INTEGER,

      -- options (flags and options)
      options TEXT,

      -- Timestamps
      sentTimestamp INTEGER,              -- senderTimestamp
      recvTimestamp INTEGER,              -- meta.timestamp

      -- Protocol metadata
      protocol TEXT NOT NULL,             -- 'meshcore' | 'meshtastic'
      connId TEXT                         -- e.g. 'meshcore-1'
    );
    CREATE INDEX idx_messages_contact ON messages(contactId);
    CREATE INDEX idx_messages_channel ON messages(channelId);
    """,
]
