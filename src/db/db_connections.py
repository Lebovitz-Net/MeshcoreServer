dbConnections = [
        """
    CREATE TABLE IF NOT EXISTS connections (
      connection_id TEXT PRIMARY KEY,
      num INTEGER,
      nodeType INTEGER DEFAULT 0,
      transport TEXT,
      status TEXT,
      FOREIGN KEY (num) REFERENCES nodes(num)
    );
    """,
]
