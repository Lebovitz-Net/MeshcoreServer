import asyncio
from ..event_emitter import EventEmitter
from .meshcore_command_queue import MeshcoreCommandQueue

_meshcore_runtime = None

def bind_mesh_runtime(runtime):
    global _meshcore_runtime
    _meshcore_runtime = runtime

def get_mesh_runtime():
    return _meshcore_runtime


class MeshcoreRequests(EventEmitter):
    instance = None

    def __init__(self, handler, interval=10000):
        super().__init__()
        self.connection = handler["connection"]
        self.queue = MeshcoreCommandQueue(handler, interval)

        if MeshcoreRequests.instance is None:
            MeshcoreRequests.instance = self

    @staticmethod
    def get_instance():
        return MeshcoreRequests.instance

    # --- High-level API calls ---
    async def get_self_info(self, timeout_ms=None):
        return await self.queue.send(lambda: self.connection.get_self_info(timeout_ms))

    async def send_advert(self, type_):
        return await self.queue.send(lambda: self.connection.send_advert(type_))

    async def send_flood_advert(self):
        return await self.queue.send(lambda: self.connection.send_flood_advert())

    async def send_zero_hop_advert(self):
        return await self.queue.send(lambda: self.connection.send_zero_hop_advert())

    async def set_advert_name(self, name):
        return await self.queue.send(lambda: self.connection.set_advert_name(name))

    async def set_advert_lat_long(self, lat, lon):
        return await self.queue.send(lambda: self.connection.set_advert_lat_long(lat, lon))

    async def set_tx_power(self, tx_power):
        return await self.queue.send(lambda: self.connection.set_tx_power(tx_power))

    # --- Messages ---
    async def send_message(self, txt_type, attempt, sender_ts, pubkey_prefix, text):
        return await self.queue.send(
            lambda: self.connection.send_message(txt_type, attempt, sender_ts, pubkey_prefix, text)
        )

    async def send_channel_message(self, txt_type, channel_idx, sender_ts, text):
        return await self.queue.send(
            lambda: self.connection.send_channel_message(txt_type, channel_idx, sender_ts, text)
        )

    async def send_channel_text_message(self, channel_idx, text):
        return await self.queue.send(lambda: self.connection.send_channel_text_message(channel_idx, text))

    async def sync_next_message(self):
        return await self.queue.send(lambda: self.connection.sync_next_message())

    async def get_waiting_messages(self):
        return await self.queue.send(lambda: self.connection.get_waiting_messages())

    # --- Contacts ---
    async def get_contacts(self, since=None):
        return await self.queue.send(lambda: self.connection.get_contacts(since))

    async def add_or_update_contact(self, public_key, type_, flags, out_path_len, out_path, adv_name, last_advert, adv_lat, adv_lon):
        return await self.queue.send(
            lambda: self.connection.add_or_update_contact(public_key, type_, flags, out_path_len, out_path, adv_name, last_advert, adv_lat, adv_lon)
        )

    async def remove_contact(self, pubkey):
        return await self.queue.send(lambda: self.connection.remove_contact(pubkey))

    async def share_contact(self, pubkey):
        return await self.queue.send(lambda: self.connection.share_contact(pubkey))

    async def export_contact(self, pubkey=None):
        return await self.queue.send(lambda: self.connection.export_contact(pubkey))

    async def import_contact(self, advert_bytes):
        return await self.queue.send(lambda: self.connection.import_contact(advert_bytes))

    # --- Channels ---
    async def get_channel(self, idx):
        return await self.queue.send(lambda: self.connection.get_channel(idx))

    async def set_channel(self, idx, name, secret):
        return await self.queue.send(lambda: self.connection.set_channel(idx, name, secret))

    async def get_channels(self):
        return await self.queue.send(lambda: self.connection.get_channels())

    # --- Device / Radio ---
    async def set_radio_params(self, freq, bw, sf, cr):
        return await self.queue.send(lambda: self.connection.set_radio_params(freq, bw, sf, cr))

    async def get_device_time(self):
        return await self.queue.send(lambda: self.connection.get_device_time())

    async def set_device_time(self, epoch_secs):
        return await self.queue.send(lambda: self.connection.set_device_time(epoch_secs))

    async def get_battery_voltage(self):
        return await self.queue.send(lambda: self.connection.get_battery_voltage())

    async def reboot(self):
        return await self.queue.send(lambda: self.connection.reboot())

    # --- Security ---
    async def export_private_key(self):
        return await self.queue.send(lambda: self.connection.export_private_key())

    async def import_private_key(self, privkey):
        return await self.queue.send(lambda: self.connection.import_private_key(privkey))

    async def sign_start(self):
        return await self.queue.send(lambda: self.connection.sign_start())

    async def sign_data(self, data):
        return await self.queue.send(lambda: self.connection.sign_data(data))

    async def sign_finish(self):
        return await self.queue.send(lambda: self.connection.sign_finish())

    # --- Loops ---
    def start_loop(self, label, fn, interval=10000):
        self.queue.start_loop(label, fn, interval)

    def stop_loop(self, label):
        self.queue.stop_loop(label)

    def close(self):
        self.connection.close()
        super().close()
