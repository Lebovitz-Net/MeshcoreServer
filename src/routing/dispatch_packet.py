from .dispatch_messages import dispatchMessages
from .dispatch_configs import dispatchConfigs
from .dispatch_contacts import dispatchContacts
from .dispatch_nodes import dispatchNodes
from .dispatch_metrics import dispatchMetrics
from .dispatch_channels import dispatchChannels
from .dispatch_mesh_packet import dispatchMeshPacket
from .dispatch_mqtt import dispatchMqtt
from .dispatch_diagnostics import dispatchDiagnostics
from external.meshcore.constants import Constants


# Build response map from Constants
response_codes = Constants.ResponseCodes
push_codes = Constants.PushCodes
all_codes = {**response_codes, **push_codes}

response_map = {value: key for key, value in all_codes.items()}


def get_type_name(type_):
    try:
        # numeric types
        if isinstance(type_, int):
            return response_map.get(type_)
        # string types
        return type_
    except Exception:
        return type_


# Merge all dispatch registries into one
dispatch_registry = {
    **dispatchMeshPacket,
    **dispatchMessages,
    **dispatchContacts,
    **dispatchConfigs,
    **dispatchNodes,
    **dispatchMetrics,
    **dispatchChannels,
    **dispatchMqtt,
    **dispatchDiagnostics,
    "default": lambda sub_packet: print(
        "[dispatchRegister] no such packet type", sub_packet.get("type")
    ),
}


def dispatch_packet(sub_packet: dict):
    if not sub_packet:
        return
    type_ = sub_packet.get("type")
    key = get_type_name(type_)
    handler = dispatch_registry.get(key)
    if handler:
        handler(sub_packet)
    else:
        print(f"[dispatchPacket] No handler for type {key}")
