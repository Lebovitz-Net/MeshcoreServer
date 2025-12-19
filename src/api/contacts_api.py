from aiohttp import web
from src.api.api_utils import safe, safe_json

class ContactsAPI:

    @safe
    async def list_contacts(self, request):
        return web.json_response(safe_json(self.query.list_contacts()))
