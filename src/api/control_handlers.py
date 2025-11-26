# handlers/control_handlers.py
from flask import jsonify
from api_utils import safe
from services_manager import restart_services   # assuming restart_services is ported separately

@safe
def restart_services_handler():
    result = restart_services()
    return jsonify(result)

handlers = {
    "restartServicesHandler": restart_services_handler,
}
