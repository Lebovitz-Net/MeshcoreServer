dbChannels = [
    """
    CREATE TABLE IF NOT EXISTS channels (
        channelIdx INTEGER PRIMARY KEY,
        channelNum INTEGER,
        nodeNum INTEGER,
        protocol INTEGER DEFAULT 0,
        name TEXT,
        role TEXT,
        psk TEXT,
        options TEXT,
        timestamp INTEGER,
        connId TEXT
    );
    """
]
