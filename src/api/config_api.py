from aiohttp import web
from src.api.api_utils import safe, safe_json

class ConfigAPI:

    @safe
    async def get_full_config(self, request):
        return web.json_response(safe_json(self.query.get_full_config()))


    @safe
    async def get_config(self, request):
        config_id = request.match_info.get("id")
        config = self.query.get_config(config_id)
        return web.json_response(safe_json(config) if config else {"error": "Config not found"}, status=200 if config else 404)


    @safe
    async def list_all_configs(self, request):
        return web.json_response(safe_json(self.query.list_all_configs()))


    @safe
    async def get_module_config(self, request):
        module_id = request.match_info.get("id")
        config = self.query.get_module_config(module_id)
        return web.json_response(safe_json(config) if config else {"error": "Module config not found"}, status=200 if config else 404)


    @safe
    async def list_all_module_configs(self, request):
        return web.json_response(safe_json(self.query.list_all_module_configs()))


    @safe
    async def get_metadata_by_key(self, request):
        key = request.match_info.get("key")
        meta = self.query.get_metadata_by_key(key)
        return web.json_response(safe_json(meta) if meta else {"error": "Metadata not found"}, status=200 if meta else 404)


    @safe
    async def list_all_metadata(self, request):
        return web.json_response(safe_json(self.query.list_all_metadata()))


    @safe
    async def list_file_info(self, request):
        return web.json_response(safe_json(self.query.list_file_info()))

