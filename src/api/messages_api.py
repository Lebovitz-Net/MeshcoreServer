from aiohttp import web
from src.api.api_utils import safe, safe_json, generate_message_id


class MessagesAPI:

    @safe
    async def list_messages(self, request):
        channel_id = request.rel_url.query.get("channelId")
        since_date = int(request.rel_url.query.get("sinceDate", 0))
        limit = int(request.rel_url.query.get("limit", 500))

        messages = self.query.list_messages(
            int(channel_id) if channel_id else None,
            since_date,
            limit,
        )

        return web.json_response(safe_json(messages))


    @safe
    async def send_message(self, request):
        body = await request.json()
        message = body.get("message")
        channel_id = body.get("channelId")
        sender = body.get("sender")

        if not message or not isinstance(message, str):
            return web.json_response({"error": "Missing or invalid payload"}, status=400)

        await self.requests.send_channel_text_message(channel_id, message)

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

        inserted = self.insert.insert_message(shaped)
        return web.json_response({"ok": True, "message": safe_json(inserted)})

