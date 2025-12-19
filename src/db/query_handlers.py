# src/db/query_handlers.py

from src.db.queries.config_queries import ConfigQueries
from src.db.queries.contact_queries import ContactQueries
from src.db.queries.device_queries import DeviceQueries
from src.db.queries.diagnostic_queries import DiagnosticQueries
from src.db.queries.message_queries import MessageQueries
from src.db.queries.metric_queries import MetricQueries
from src.db.queries.node_queries import NodeQueries


class QueryHandlers(
    ConfigQueries,
    ContactQueries,
    DeviceQueries,
    DiagnosticQueries,
    MessageQueries,
    MetricQueries,
    NodeQueries,
):
    """
    Aggregates all query-related mixins into a single handler object.
    Mirrors the InsertHandlers architecture.
    """

    __slots__ = ("db",)

    def __init__(self, db):
        self.db = db

    def __getitem__(self, name: str):
        """
        Allow dictionary-style access to query handlers.

        Supports:
        - Exact method names: "list_nodes"
        - (Optional) camelCase compatibility if ever needed
        """
        fn = getattr(self, name, None)

        # Optional camelCase → snake_case support
        if fn is None and any(c.isupper() for c in name):
            snake = []
            for c in name:
                snake.append("_" + c.lower() if c.isupper() else c)
            snake_name = "".join(snake)
            fn = getattr(self, snake_name, None)

        if fn is None:
            raise KeyError(f"No query handler named '{name}'")

        return fn

    def __contains__(self, name: str):
        """
        Support: `"list_nodes" in queries`.
        """
        return hasattr(self, name)

    def __iter__(self):
        """
        Iterate over all query handler names.
        By convention, any public callable method is a handler.
        """
        for name in dir(self):
            if name.startswith("_"):
                continue
            attr = getattr(self, name)
            if callable(attr):
                yield name
