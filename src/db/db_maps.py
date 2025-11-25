dbMaps =[
    
    """
    CREATE TABLE IF NOT EXISTS device_ip_map (
      source_ip TEXT PRIMARY KEY,
      num INTEGER NOT NULL,
      nodeType INTEGER DEFAULT 0,
      device_id TEXT,
      last_seen INTEGER NOT NULL
    );
    """,
]
