# src/db/insert_handlers.py

from src.db.inserts.message_inserts import MessageInserts
from src.db.inserts.channel_inserts import ChannelInserts
from src.db.inserts.config_inserts import ConfigInserts
from src.db.inserts.contact_inserts import ContactInserts
from src.db.inserts.device_inserts import DeviceInserts
from src.db.inserts.diagnostic_inserts import DiagnosticInserts
from src.db.inserts.metric_inserts import MetricInserts
from src.db.inserts.node_inserts import NodeInserts


class InsertHandlers(
    MessageInserts,
    ChannelInserts,
    ConfigInserts,
    ContactInserts,
    DeviceInserts,
    DiagnosticInserts,
    MetricInserts,
    NodeInserts,
):
    __slots__ = ("db", "sse_emitter")

    def __init__(self, db, sse_emitter, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = db
        self.sse_emitter = sse_emitter

    def __getitem__(self, name: str):
        # Try exact match
        fn = getattr(self, name, None)

        # Try camelCase → snake_case
        if fn is None and any(c.isupper() for c in name):
            snake = []
            for c in name:
                snake.append("_" + c.lower() if c.isupper() else c)
            snake_name = "".join(snake)
            fn = getattr(self, snake_name, None)

        if fn is None:
            raise KeyError(f"No insert handler named '{name}'")

        return fn

    def __contains__(self, name: str):
        return hasattr(self, name)

    def __iter__(self):
        for name in dir(self):
            if name.startswith("insert_") or name.startswith("upsert_"):
                yield name

