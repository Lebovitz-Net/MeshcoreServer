import json
from src.Utils.packet_utils import get_text_from_key, hash_public_key, get_public_key_value
from db.insert_handlers import insertHandlers


def handle_contact(packet: dict):
    data, meta = packet["data"], packet["meta"]

    public_key = data["publicKey"]
    shaped = {
        "contactId": data["advName"],
        "type": data["type"],
        "name": data["advName"],
        "publicKey": get_text_from_key(public_key),
        "protocol": "meshcore",
        "nodeNum": hash_public_key(public_key),
        "shortName": None,
        "times": json.dumps({"lastHeard": data["lastAdvert"], "lastMod": data["lastMod"]}),
        "options": json.dumps({
            "outPath": data["outPath"],
            "outPathLen": data["outPathLen"],
            "flags": data["flags"],
        }),
        "position": json.dumps({"lat": data["advLat"], "lon": data["advLon"]}),
        **meta,
    }

    insertHandlers.insertUsers(shaped)


def handle_contacts_start(packet: dict):
    print(".../ContactsStart")


def handle_end_of_contacts(packet: dict):
    print(".../EndOfContacts")


dispatchContacts = {
    "Contact": handle_contact,
    "ContactsStart": handle_contacts_start,
    "EndOfContacts": handle_end_of_contacts,
}
