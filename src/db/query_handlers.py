from src.db.queries.node_queries import node_queries
from src.db.queries.config_queries import config_queries
from src.db.queries.device_queries import device_queries
from src.db.queries.metric_queries import metric_queries
from src.db.queries.diagnostic_queries import diagnostic_queries
from src.db.queries.message_queries import message_queries
from src.db.queries.contact_queries import contact_queries

# Merge all query dicts into one registry
query_handlers = {
    **node_queries,
    **config_queries,
    **device_queries,
    **metric_queries,
    **diagnostic_queries,
    **message_queries,
    **contact_queries,
}

def handle_query(name: str, *args, **kwargs):
    """
    Dispatch query by name. Example:
        handle_query("list_nodes")
        handle_query("get_config", 42)
    """
    fn = query_handlers.get(name)
    if not fn:
        print(f"[queryHandlers] Unknown query: {name}")
        return None

    try:
        return fn(*args, **kwargs)
    except Exception as err:
        print(f"[queryHandlers] Error in {name}: {err}")
        return None
