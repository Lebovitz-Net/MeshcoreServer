from aiohttp import web
from src.api.api_utils import safe

class ControlAPI:

    @safe
    async def restart_services(self, request):
        return web.json_response(self.restart_services())

