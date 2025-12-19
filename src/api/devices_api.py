from aiohttp import web
from src.api.api_utils import safe, safe_json

class DevicesAPI:

    @safe
    async def list_devices(self, request):
        return web.json_response(safe_json(self.query.list_devices()))


    @safe
    async def get_device(self, request):
        device_id = request.match_info.get("device_id")
        device = self.query.get_device(device_id)
        if not device:
            return web.json_response({"error": "Device not found"}, status=404)

        settings = self.query.list_device_settings(device_id)
        return web.json_response(safe_json({**device, "settings": settings}))


    @safe
    async def get_device_setting(self, request):
        device_id = request.match_info.get("device_id")
        config_type = request.match_info.get("config_type")
        setting = self.query.get_device_setting(device_id, config_type)
        return web.json_response(safe_json(setting) if setting else {"error": "Setting not found"}, status=200 if setting else 404)
