
from src.api.system_api import SystemAPI
from src.api.nodes_api import NodesAPI
from src.api.messages_api import MessagesAPI
from src.api.contacts_api import ContactsAPI
from src.api.config_api import ConfigAPI
from src.api.devices_api import DevicesAPI
from src.api.diagnostics_api import DiagnosticsAPI
from src.api.metrics_api import MetricsAPI
from src.api.control_api import ControlAPI
from api.services_api import ServicesManager
from db.query_handlers import QueryHandlers


class APIHandlers(
    SystemAPI,
    NodesAPI,
    MessagesAPI,
    ContactsAPI,
    ConfigAPI,
    DevicesAPI,
    DiagnosticsAPI,
    MetricsAPI,
    ControlAPI,
    ServicesManager,
):
    def __init__(self, dispatcher, requests):
        # Initialize each base class with the same signature
        super().__init__()
        self.db = dispatcher.database
        self.insert = dispatcher.insert_handlers
        self.requests = requests
        self.query = QueryHandlers(self.db)

