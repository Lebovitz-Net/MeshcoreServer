# handlers/__init__.py
from . import nodes_handlers, messages_handlers, metrics_handlers, devices_handlers
from . import system_handlers, diagnostics_handlers, control_handlers, config_handlers, contacts_handlers

api_handlers = {
    **nodes_handlers.handlers,
    **messages_handlers.handlers,
    **metrics_handlers.handlers,
    **devices_handlers.handlers,
    **system_handlers.handlers,
    **diagnostics_handlers.handlers,
    **control_handlers.handlers,
    **config_handlers.handlers,
    **contacts_handlers.handlers,
}
