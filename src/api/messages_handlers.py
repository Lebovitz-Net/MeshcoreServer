# handlers/messages_handlers.py
from flask import jsonify, request
from api_utils import safe, generate_message_id
from src.db.query_handlers import query_handlers
from src.db.insert_handlers import insert_handlers
from MeshCore.meshcoreRequests import MeshcoreRequests

@safe
def list_messages_handler():
    channel_id = request.args.get("channelId")
    since_date = int(request.args.get("sinceDate", 0))
    limit = request.args.get("limit")
    limit = int(limit) if limit else None

    messages = query_handlers["listMessages"]({
        "channelId": int(channel_id) if channel_id else None,
        "sinceDate": since_date,
        "limit": limit,
    })
    print(f"[listMessagesHandler] returning {len(messages)} messages")
    return jsonify(messages)

@safe
def send_message_handler():
    body = request.json or {}
    message = body.get("message")
    channel_id = body.get("channelId")
    sender = body.get("sender")

    if not message or not isinstance(message, str):
        return jsonify({"error": "Missing or invalid payload"}), 400

    request_obj = MeshcoreRequests.get_instance()
    request_obj.send_channel_text_message(channel_id, message)

    shaped = {
        "contactId": sender,
        "messageId": generate_message_id(body),
        "channelId": channel_id,
        "fromNodeNum": body.get("fromNodeNum"),
        "toNodeNum": body.get("toNodeNum"),
        "message": f"{sender}: {message}",
        "recvTimestamp": body.get("recvTimestamp"),
        "sentTimestamp": body.get("sentTimestamp"),
        "protocol": body.get("protocol"),
        "sender": sender,
        "mentions": body.get("mentions"),
        "options": body.get("options"),
    }

    inserted = insert_handlers["insertMessage"](shaped)
    return jsonify({"ok": True, "message": inserted})

handlers = {
    "listMessagesHandler": list_messages_handler,
    "sendMessageHandler": send_message_handler,
}
