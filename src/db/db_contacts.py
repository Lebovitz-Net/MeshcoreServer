dbContacts = [
"""
CREATE TABLE IF NOT EXISTS users (
    contactId TEXT PRIMARY KEY, -- advName or String nodeNum
    type INTEGER DEFAULT 0,     -- type
    name TEXT,                  -- advName, longname
    publicKey TEXT,             -- publicKey
    timestamp INTEGER,
    protocol INTEGER,

    -- Meshtastic
    nodeNum INTEGER,            -- nodeNum, or publicKey Hash
    shortName TEXT,             -- shortName Meshtastic

    times TEXT,                 -- lastHeard, lastMod, updateAt
    options TEXT,               -- hwModel, macaddr, ismessageable, outPath, outPathLen, flags
    position TEXT,              -- advlat, advlon or latitude, longitude from position
    connId TEXT
    );
    """,

"""
CREATE TABLE IF NOT EXISTS positions (
    contactid INTEGER PRIMARY KEY,
    fromNodeNum INTEGER NOT NULL,
    fromNodeType INTEGER DEFAULT 0,
    toNodeNum INTEGER NOT NULL DEFAULT 4294967295,
    toNodeType INTEGER DEFAULT 0,
    latitude REAL,
    longitude REAL,
    altitude REAL,
    timestamp INTEGER
    );
    """,
]