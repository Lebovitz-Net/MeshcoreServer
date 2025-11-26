import json
from src.meshtastic.utils.packet_utils import get_text_from_key, hash_public_key, get_public_key_value
from db.insert_handlers import insertHandlers
from meshcore.meshcore_requests import MeshcoreRequests
from utils import normalize_in
from api.api_utils import generate_message_id, extract_sender_and_mentions
from events.overlay_emitter import emitOverlay
from events.event_emitter import emitEvent
from meshcore.utils.string_utils import decode_node_info

insert_message = insertHandlers.insertMessage


def handle_sent(packet: dict):
    print(".../dispatchMessages sent", packet)


def handle_msg_waiting(packet: dict):
    data, meta = packet["data"], packet["meta"]
    print(".../dispatchMessages MsgWaiting", packet)
    request = MeshcoreRequests.get_instance()
    asyncio.create_task(request.get_waiting_messages())


def handle_advert(packet: dict):
    key = packet.get("data", {}).get("data", {}).get("publicKey")
    print(".../dispatchMessages Advert key is", get_text_from_key(key))


def handle_channel_msg_recv(packet: dict):
    data, meta = packet["data"], packet["meta"]
    text, txt_type, path_len = data["text"], data["txtType"], data["pathLen"]
    sender, mentions = extract_sender_and_mentions(text)

    if sender is None:
        print("[dispatchMessage] skipping Message cannot extract sender", packet)
        return

    print(".../dispatchMessages Channel Message is", text)

    shaped = {
        "contactId": sender,
        "messageId": generate_message_id(packet),
        "channelId": data.get("channelIdx", "default"),
        "fromNodeNum": data.get("from", 0),
        "toNodeNum": data.get("to"),
        "message": text,
        "recvTimestamp": meta["timestamp"],
        "sentTimestamp": normalize_in(data["senderTimestamp"]),
        "protocol": "meshcore",
        "sender": sender,
        "mentions": json.dumps(mentions),
        "options": json.dumps({"txtType": txt_type, "pathLen": path_len}),
    }

    insert_message(shaped)


def handle_no_more_messages(packet: dict):
    print(".../dispatchMessages NoMoreMessages")


def handle_contact_msg_received(packet: dict):
    print(".../dispatchMessages ContactMsgRev", packet)


def handle_message(sub_packet: dict):
    packet, meta = sub_packet["packet"], sub_packet["meta"]
    from_node_num, to_node_num, channel, timestamp, conn_id = (
        meta["fromNodeNum"],
        meta["toNodeNum"],
        meta.get("channel", 0),
        meta["timestamp"],
        meta["connId"],
    )
    data = packet["data"]
    id_, decoded, reply_id, want_reply, want_ack = (
        data["id"],
        data.get("decoded"),
        data.get("replyId"),
        data.get("wantReply"),
        data.get("wantAck"),
    )
    message = decoded.get("payload") if decoded else None

    insertHandlers.insertMessage({
        "contactId": str(from_node_num),
        "messageId": id_,
        "channelId": channel,
        "message": message,
        "fromNodeNum": from_node_num,
        "toNodeNum": to_node_num,
        "timestamp": timestamp,
        "protocol": "Meshtastic",
        "sender": reply_id,
        "options": json.dumps({"replyId": reply_id, "wantReply": want_reply, "wantAck": want_ack}),
        "connId": conn_id,
    })

    emitOverlay("message", sub_packet)
    emitEvent("messageReceived", sub_packet)
    print("[dispatchMessages] message")


def handle_Message(sub_packet: dict):
    print("[dispatchMessage] Message", sub_packet)


def handle_text(sub_packet: dict):
    data, meta = sub_packet["data"], sub_packet["meta"]
    print("[dispatchMessage] text", sub_packet, decode_node_info(data["topic"]))


def handle_client_notification(sub_packet: dict):
    print("[dispatchMessage] ClientNotification")


def handle_client_notification_lower(sub_packet: dict):
    print("[dispatchMessage] clientNotification")


dispatchMessages = {
    "Sent": handle_sent,
    "MsgWaiting": handle_msg_waiting,
    "Advert": handle_advert,
    "ChannelMsgRecv": handle_channel_msg_recv,
    "NoMoreMessages": handle_no_more_messages,
    "ContactMsgReceived": handle_contact_msg_received,
    "message": handle_message,
    "Message": handle_Message,
    "text": handle_text,
    "ClientNotification": handle_client_notification,
    "clientNotification": handle_client_notification_lower,
}
