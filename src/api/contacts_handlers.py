# handlers/contacts_handlers.py
from flask import jsonify
from api_utils import safe
from src.db.query_handlers import query_handlers

@safe
def list_contacts_handler():
    return jsonify(query_handlers["listContacts"]())

handlers = {
    "listContactsHandler": list_contacts_handler,
}
