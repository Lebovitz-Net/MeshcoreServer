dbMetrics = [
   """
   CREATE TABLE IF NOT EXISTS device_metrics (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      fromNodeNum INTEGER NOT NULL,
      fromNodeType INTEGER DEFAULT 0,
      toNodeNum INTEGER NOT NULL DEFAULT 4294967295,
      toNodeType INTEGER DEFAULT 0,
      batteryLevel REAL,
      txPower INTEGER,
      uptime INTEGER,
      cpuTemp REAL,
      memoryUsage REAL,
      timestamp INTEGER,
      FOREIGN KEY (fromNodeNum) REFERENCES nodes(num)
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS telemetry (
      telemetryId INTEGER PRIMARY KEY AUTOINCREMENT,
      fromNodeNum INTEGER NOT NULL,
      fromNodeType INTEGER DEFAULT 0,
      toNodeNum INTEGER NOT NULL DEFAULT 4294967295,
      toNodeType INTEGER DEFAULT 0,
      metric TEXT,
      value REAL,
      timestamp INTEGER,
      FOREIGN KEY (fromNodeNum) REFERENCES nodes(num)
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS event_emissions (
      event_id INTEGER PRIMARY KEY AUTOINCREMENT,
      num INTEGER,
      nodeType INTEGER DEFAULT 0,
      event_type TEXT,
      details TEXT,
      timestamp INTEGER,
      FOREIGN KEY (num) REFERENCES nodes(num)
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS queue_status (
      status_id INTEGER PRIMARY KEY AUTOINCREMENT,
      num INTEGER,
      nodeType INTEGER DEFAULT 0,
      res INTEGER,
      free INTEGER,
      maxlen INTEGER,
      meshPacketId INTEGER,
      timestamp INTEGER DEFAULT (strftime('%s','now')),
      connId TEXT,
      FOREIGN KEY (num) REFERENCES nodes(num)
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS environment_metrics (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      fromNodeNum INTEGER NOT NULL,
      fromNodeType INTEGER DEFAULT 0,
      toNodeNum INTEGER NOT NULL DEFAULT 4294967295,
      toNodeType INTEGER DEFAULT 0,
      temperature REAL,
      humidity REAL,
      pressure REAL,
      lightLevel REAL,
      timestamp INTEGER,
      FOREIGN KEY (fromNodeNum) REFERENCES nodes(num)
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS air_quality_metrics (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      fromNodeNum INTEGER NOT NULL,
      fromNodeType INTEGER DEFAULT 0,
      toNodeNum INTEGER NOT NULL DEFAULT 4294967295,
      toNodeType INTEGER DEFAULT 0,
      pm25 REAL,
      pm10 REAL,
      co2 REAL,
      voc REAL,
      ozone REAL,
      timestamp INTEGER,
      FOREIGN KEY (fromNodeNum) REFERENCES nodes(num)
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS power_metrics (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      fromNodeNum INTEGER NOT NULL,
      fromNodeType INTEGER DEFAULT 0,
      toNodeNum INTEGER NOT NULL DEFAULT 4294967295,
      toNodeType INTEGER DEFAULT 0,
      voltage REAL,
      current REAL,
      power REAL,
      energy REAL,
      frequency REAL,
      timestamp INTEGER,
      FOREIGN KEY (fromNodeNum) REFERENCES nodes(num)
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS local_stats (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      fromNodeNum INTEGER NOT NULL,
      fromNodeType INTEGER DEFAULT 0,
      toNodeNum INTEGER NOT NULL DEFAULT 4294967295,
      toNodeType INTEGER DEFAULT 0,
      snr REAL,
      rssi REAL,
      hopCount INTEGER,
      linkQuality REAL,
      packetLoss REAL,
      timestamp INTEGER,
      FOREIGN KEY (fromNodeNum) REFERENCES nodes(num)
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS health_metrics (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      fromNodeNum INTEGER NOT NULL,
      fromNodeType INTEGER DEFAULT 0,
      toNodeNum INTEGER NOT NULL DEFAULT 4294967295,
      toNodeType INTEGER DEFAULT 0,
      cpuTemp REAL,
      diskUsage REAL,
      memoryUsage REAL,
      uptime INTEGER,
      loadAvg REAL,
      timestamp INTEGER,
      FOREIGN KEY (fromNodeNum) REFERENCES nodes(num)
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS host_metrics (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      fromNodeNum INTEGER NOT NULL,
      fromNodeType INTEGER DEFAULT 0,
      toNodeNum INTEGER NOT NULL DEFAULT 4294967295,
      toNodeType INTEGER DEFAULT 0,
      hostname TEXT,
      uptime INTEGER,
      loadAvg REAL,
      osVersion TEXT,
      bootTime INTEGER,
      timestamp INTEGER,
      FOREIGN KEY (fromNodeNum) REFERENCES nodes(num)
    );
    """,
]
