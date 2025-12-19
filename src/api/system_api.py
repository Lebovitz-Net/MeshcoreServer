# handlers/system_handlers.py
from aiohttp import web
from src.api.api_utils import safe
from src.config.config import config
import time

class SystemAPI:

    @safe
    async def health(self, request):
        return web.Response(text="MeshManager v2 is running")


    @safe
    async def get_config(self, request):
        return web.json_response(config)


    @safe
    async def get_version(self, request):
        return web.json_response({
            "version": "1.0.0",
            "buildDate": __import__("datetime").datetime.utcnow().isoformat()
        })


    @safe
    async def get_health(self, request):
        return web.json_response({
            "status": "ok",
            "uptime": time.time()
        })
