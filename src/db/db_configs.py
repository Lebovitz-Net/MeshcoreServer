dbConfigs = [
    """
    CREATE TABLE IF NOT EXISTS devices (
      device_id TEXT PRIMARY KEY,
      num INTEGER,
      nodeType INTEGER DEFAULT 0,
      conn_id TEXT,
      device_type TEXT DEFAULT 'meshtastic',
      last_seen INTEGER DEFAULT (strftime('%s','now'))
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS device_settings (
      device_id TEXT NOT NULL,
      num INTEGER,
      nodeType INTEGER DEFAULT 0,
      config_type TEXT NOT NULL,
      config_json TEXT NOT NULL,
      conn_id TEXT,
      updated_at INTEGER NOT NULL,
      PRIMARY KEY (device_id, config_type)
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS device_meta (
      device_id TEXT REFERENCES devices(device_id),
      reboot_count INTEGER,
      min_app_version INTEGER,
      pio_env TEXT,
      firmware_version TEXT,
      hw_model INTEGER,
      conn_id TEXT,
      updated_at INTEGER DEFAULT (strftime('%s','now')),
      timestamp INTEGER DEFAULT (strftime('%s','now'))
    );
    """
]
