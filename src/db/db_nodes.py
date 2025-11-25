dbNodes = [
    """
    CREATE TABLE IF NOT EXISTS my_info (
      myNodeNum INTEGER PRIMARY KEY,  -- hash from primaryKey in meshcore
      name TEXT,
      shortName TEXT,
      type INTEGER DEFAULT 0,         -- type
      options TEXT,                   -- deviceId, RebootCount, minAppVersion, pioEnv, 
                                      -- radioFreq, radioBw, radioSf, radioCr, txPower, maxTxPower
                                      -- advLat, advLon manualAddContact       
      publicKey TEXT,
      protocol TEXT,               -- 'meshtastic', or 'meshcore'
      currentIP TEXT,
      connId TEXT,
      timestamp INTEGER
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS nodes ( -- not used in meshcore
      num INTEGER PRIMARY KEY,
      nodeType INTEGER DEFAULT 0,
      label TEXT,
      device_id TEXT,
      last_seen INTEGER,
      viaMqtt BOOLEAN,
      hopsAway INTEGER,
      lastHeard INTEGER
    );
    """,
]
