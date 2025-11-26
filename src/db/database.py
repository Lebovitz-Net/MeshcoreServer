# src/meshtastic/utils/database.py

import os
import sqlite3
from pathlib import Path

from src.db.db_nodes import db_nodes
from src.db.db_metrics import db_metrics
from src.db.db_messages import db_messages
from src.db.db_maps import db_maps
from src.db.db_diagnostics import db_diagnostics
from src.db.db_connections import db_connections
from src.db.db_configs import db_configs
from src.db.db_contacts import db_contacts
from src.db.db_channels import db_channels

# --- Combined schema tables ---
tables = (
    db_contacts
    + db_channels
    + db_configs
    + db_connections
    + db_diagnostics
    + db_maps
    + db_messages
    + db_metrics
    + db_nodes
)

# --- DB path ---
base_dir = Path(__file__).resolve().parent
db_path = base_dir.joinpath("../../data/meshmanager.db").resolve()
print(f"[db] Opening DB at: {db_path}")

# --- Boolean helpers ---
TRUE = 1
FALSE = 0

def db_boolean(val: bool) -> int:
    return TRUE if val else FALSE

# --- Open connection ---
db = sqlite3.connect(db_path)
db.row_factory = sqlite3.Row  # optional: access columns by name


def build_database(conn: sqlite3.Connection) -> None:
    """
    Create all tables defined in schema lists.
    """
    cursor = conn.cursor()
    for i, sql in enumerate(tables, start=1):
        try:
            cursor.execute(sql)
            table_name = None
            if "CREATE TABLE IF NOT EXISTS" in sql:
                import re
                match = re.search(r"CREATE TABLE IF NOT EXISTS (\w+)", sql)
                table_name = match.group(1) if match else f"Table {i}"
            print(f"[DB] Created: {table_name}")
        except Exception as err:
            print(f"[DB] Error creating table {i}: {err}")


def apply_migrations(conn: sqlite3.Connection, db_schemas: list[dict]) -> None:
    """
    Apply schema migrations if newer versions exist.
    db_schemas should be a list of dicts: {"version": int, "tables": [sql, ...]}
    """
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT value FROM schema_meta WHERE key = 'schemaVersion'")
        row = cursor.fetchone()
        current_version = int(row["value"]) if row else 0
    except Exception:
        current_version = 0

    for schema in db_schemas:
        version = schema.get("version")
        schema_tables = schema.get("tables", [])
        if version > current_version:
            print(f"[DB] Applying schema version {version}")
            for sql in schema_tables:
                try:
                    cursor.execute(sql)
                    print(f"[DB] Executed: {sql.splitlines()[0].strip()}")
                except Exception as err:
                    print(f"[DB] Error: {err}")
            cursor.execute(
                "REPLACE INTO schema_meta (key, value) VALUES ('schemaVersion', ?)",
                (version,),
            )
            conn.commit()
            print(f"[DB] Updated schema version to {version}")
