# src/db/insertHandlers.py

from src.db.inserts.channel_inserts import channel_inserts
from src.db.inserts.config_inserts import config_inserts
from src.db.inserts.contact_inserts import contact_inserts
from src.db.inserts.device_inserts import device_inserts
from src.db.inserts.diagnostic_inserts import diagnostic_inserts
from src.db.inserts.message_inserts import message_inserts
from src.db.inserts.metric_inserts import metric_inserts
from src.db.inserts.node_inserts import node_inserts


# Merge all insert dicts into one registry
insert_handlers = {
    **channel_inserts,
    **config_inserts,
    **contact_inserts,
    **device_inserts,
    **diagnostic_inserts,
    **message_inserts,
    **metric_inserts,
    **node_inserts,
}


def handle_insert(name: str, payload: dict, *args, **kwargs):
    """
    Dispatch insert by name. Example:
        handle_insert("insert_node", {"num": 123, "label": "Test"})
    """
    fn = insert_handlers.get(name)
    if not fn:
        print(f"[insertHandlers] Unknown insert function: {name}")
        return None

    try:
        # Some inserts (like insert_node_metrics) expect two args
        return fn(payload, *args, **kwargs)
    except Exception as err:
        print(f"[insertHandlers] Error in {name}: {err}")
        return None
