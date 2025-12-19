# src/routing/dispatch_packet.py

import asyncio
import threading
from src.db.database import db
from src.db.insert_handlers import InsertHandlers
from meshcore_py.constants import Constants
from meshcore_py.events import EventEmitter

from .dispatch_messages import DispatchMessages
from .dispatch_configs import DispatchConfigs
from .dispatch_contacts import DispatchContacts
from .dispatch_nodes import DispatchNodes
from .dispatch_metrics import DispatchMetrics
from .dispatch_channels import DispatchChannels
from .dispatch_mqtt import DispatchMqtt
from .dispatch_diagnostics import DispatchDiagnostics
from .dispatch_utils import to_snake_case
from decode_meshpacket import decode_meshpacket


class DispatchPacket(
    DispatchMessages,
    DispatchConfigs,
    DispatchContacts,
    DispatchNodes,
    DispatchMetrics,
    DispatchChannels,
    DispatchMqtt,
    DispatchDiagnostics,
    EventEmitter,
):
    def __init__(self, sse_emitter, request):
        EventEmitter.__init__(self)
        self.response_map = self._build_response_map()
        self._lock = threading.RLock()
        self.database = db
        self.insert_handlers = InsertHandlers(db,  sse_emitter)
        self.request = request

    def _build_response_map(self):
        response_codes = Constants.ResponseCodes
        push_codes = Constants.PushCodes
        all_codes = {
            **{
                k: v
                for k, v in vars(response_codes).items()
                if not k.startswith("__")
            },
            **{
                k: v
                for k, v in vars(push_codes).items()
                if not k.startswith("__")
            },
        }
        # value (int) -> key (UPPER_SNAKE)
        return {value: key for key, value in all_codes.items()}

    def get_type_name(self, type_):
        """
        For Meshcore (int): resolve to UPPER_SNAKE name via Constants.
        For Meshtastic (str): return as-is (expected to already be snake_case or similar).
        """
        if isinstance(type_, int):
            return self.response_map.get(type_)
        return type_

    def dispatch_packet(self, sub_packet: dict):
        """
        Unified dispatch entrypoint.

        sub_packet must contain:
          - "type": either int (meshcore code) or str (meshtastic/proto type)
          - "data": handler-specific data
          - "meta": meta info (fromNodeNum, connId, etc.)
        """
        if not sub_packet:
            return

        raw_type = sub_packet["type"]
        type_name = self.get_type_name(raw_type)
        if not type_name:
            print(f"[DispatchPacket] Unknown type: {raw_type}")
            return

        handler_name = to_snake_case(type_name)
        handler = getattr(self, handler_name, None)

        with self._lock:
            if handler:
                try:
                    handler(sub_packet)
                except Exception as err:
                    import traceback
                    print(f"[DispatchPacket] Handler {handler_name} failed:", err)
                    traceback.print_exc()
                else:
                    # Emit normalized snake_case event name
                    self.emit(handler_name, sub_packet)
            else:
                print(f"[DispatchPacket] No handler for type {handler_name}")

    def handle_mesh_packet(self, packet: dict):
        """
        Meshtastic: raw mesh packet -> processed sub_packet -> dispatch.
        """
        result = decode_meshpacket(packet)
        if result:
            self.dispatch_packet(result)

    def handle_data(self, packet: dict):
        sub_packet = packet.get("data")
        return sub_packet

    def handle_decoded(self, packet: dict):
        # Reserved hook if you want to dispatch decoded-only later
        pass

    def get_database(self):
        return self.database
    
    def get_insert_handlers(self):
        return self.insert_handlers

# --- Eager singleton instance created at import time ---
