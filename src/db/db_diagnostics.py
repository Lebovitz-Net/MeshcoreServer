dbDiagnostics = [
    """
    CREATE TABLE IF NOT EXISTS log_records (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      num INTEGER,
      nodeType INTEGER DEFAULT 0,
      packetType TEXT NOT NULL DEFAULT 'logRecord',
      message TEXT NOT NULL,
      timestamp INTEGER NOT NULL,
      connId TEXT,
      decodeStatus TEXT DEFAULT 'pending'
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS packet_logs (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      num INTEGER,
      nodeType INTEGER DEFAULT 0,
      packet_type TEXT NOT NULL,
      timestamp INTEGER NOT NULL,
      raw_payload TEXT
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS metadata (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      num INTEGER,
      nodeType INTEGER DEFAULT 0,
      firmwareVersion TEXT,
      deviceStateVersion INTEGER,
      canShutdown BOOLEAN,
      hasWifi BOOLEAN,
      hasBluetooth BOOLEAN,
      hwModel INTEGER,
      hasPKC BOOLEAN,
      excludedModules INTEGER,
      FOREIGN KEY (num) REFERENCES my_info(myNodeNum)
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS config (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      num INTEGER NOT NULL,
      nodeType INTEGER DEFAULT 0,
      timestamp INTEGER,
      type TEXT NOT NULL,
      payload TEXT NOT NULL,
      device_id TEXT,
      conn_Id TEXT,
      FOREIGN KEY (num) REFERENCES my_info(myNodeNum)
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS module_config (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      num INTEGER NOT NULL,
      nodeType INTEGER DEFAULT 0,
      timestamp INTEGER,
      type TEXT NOT NULL,
      payload TEXT NOT NULL,
      device_id TEXT,
      conn_Id TEXT,
      FOREIGN KEY (num) REFERENCES my_info(myNodeNum)
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS file_info (
      file_info_id INTEGER PRIMARY KEY AUTOINCREMENT,
      num INTEGER,
      nodeType INTEGER DEFAULT 0,
      filename TEXT,
      size INTEGER,
      mime_type TEXT,
      description TEXT,
      timestamp INTEGER DEFAULT (strftime('%s','now')),
      conn_id TEXT,
      FOREIGN KEY (num) REFERENCES nodes(num)
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS trace_logs (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      connId TEXT,
      nodeNum INTEGER,
      packetType INTEGER,
      tag INTEGER,
      pathLen INTEGER,
      lastSnr REAL,
      pathHashes TEXT,
      pathSnrs TEXT,
      timestamp INTEGER
    );
    """,
]
