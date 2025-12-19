# src/routing/dispatch_contacts.py

import json
from src.utils import get_text_from_key, hash_public_key, get_public_key_value


class DispatchContacts:
    def contact(self, packet: dict):
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
            "times": json.dumps({
                "lastHeard": data["lastAdvert"],
                "lastMod": data["lastMod"],
            }),
            "options": json.dumps({
                "outPath": data["outPath"].hex(),
                "outPathLen": data["outPathLen"],
                "flags": data["flags"],
            }),
            "position": json.dumps({
                "lat": data["advLat"],
                "lon": data["advLon"],
            }),
            **meta,
        }

        self.insert_handlers.insert_users(shaped)

    def contacts_start(self, packet: dict):
        print(".../ContactsStart")

    def end_of_contacts(self, packet: dict):
        print(".../EndOfContacts")
