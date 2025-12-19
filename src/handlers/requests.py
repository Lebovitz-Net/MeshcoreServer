import asyncio
from meshcore_py.events import EventEmitter
from src.handlers.command_queue import CommandQueue

_runtime = None

def bind_mesh_runtime(runtime):
    global _runtime
    _runtime = runtime

def get_mesh_runtime():
    return _runtime


class Requests(EventEmitter):
    instance = None

    def __init__(self, timeout_ms=10000):
        super().__init__()
        self.queue = None
        self.meshcore_connection = None
        self.meshtastic_connection = None
        self.timeout_ms = timeout_ms

        if Requests.instance is None:
            Requests.instance = self

    @staticmethod
    def get_instance():
        return Requests.instance
    
    def start_requests(self, meshcore, meshtastic):
        self.meshcore_connection = meshcore.tcp
        self.meshtastic_connection = meshtastic.connection
        self.queue = CommandQueue(meshcore.on, self.timeout_ms)

    async def get_self_info(self, timeout_ms=None):
        def fn():
            coro = self.meshcore_connection.get_self_info(timeout_ms)
            return coro
        return await self.queue.send(fn)

    async def send_advert(self, type_):
        return await self.queue.send(lambda _: self.meshcore_connection.send_advert(type_=0))

    async def send_flood_advert(self):
        return await self.queue.send(lambda: self.meshcore_connection.send_flood_advert())

    async def send_zero_hop_advert(self):
        return await self.queue.send(lambda: self.meshcore_connection.send_zero_hop_advert())

    async def set_advert_name(self, name):
        return await self.queue.send(lambda: self.meshcore_connection.set_advert_name(name))

    async def set_advert_lat_long(self, lat, lon):
        return await self.queue.send(lambda: self.meshcore_connection.set_advert_lat_long(lat, lon))

    async def set_tx_power(self, tx_power):
        return await self.queue.send(lambda: self.meshcore_connection.set_tx_power(tx_power))

    # --- Messages ---
    async def send_message(self, txt_type, attempt, sender_ts, pubkey_prefix, text):
        return await self.queue.send(
            lambda: self.meshcore_connection.send_message(txt_type, attempt, sender_ts, pubkey_prefix, text)
        )

    async def send_channel_message(self, txt_type, channel_idx, sender_ts, text):
        return await self.queue.send(
            lambda: self.meshcore_connection.send_channel_message(txt_type, channel_idx, sender_ts, text)
        )

    async def send_channel_text_message(self, channel_idx, text):
        return await self.queue.send(lambda: self.meshcore_connection.send_channel_text_message(channel_idx, text))

    async def sync_next_message(self):
        return await self.queue.send(lambda: self.meshcore_connection.sync_next_message())

    async def get_waiting_messages(self):
        return await self.queue.send(lambda: self.meshcore_connection.get_waiting_messages())

    # --- Contacts ---
    async def get_contacts(self, since=None):
        return await self.queue.send(lambda: self.meshcore_connection.get_contacts(since))

    async def add_or_update_contact(self, public_key, type_, flags, out_path_len, out_path, adv_name, last_advert, adv_lat, adv_lon):
        return await self.queue.send(
            lambda: self.meshcore_connection.add_or_update_contact(public_key, type_, flags, out_path_len, out_path, adv_name, last_advert, adv_lat, adv_lon)
        )

    async def remove_contact(self, pubkey):
        return await self.queue.send(lambda: self.meshcore_connection.remove_contact(pubkey))

    async def share_contact(self, pubkey):
        return await self.queue.send(lambda: self.meshcore_connection.share_contact(pubkey))

    async def export_contact(self, pubkey=None):
        return await self.queue.send(lambda: self.meshcore_connection.export_contact(pubkey))

    async def import_contact(self, advert_bytes):
        return await self.queue.send(lambda: self.meshcore_connection.import_contact(advert_bytes))

    # --- Channels ---
    async def get_channel(self, idx):
        return await self.queue.send(lambda: self.meshcore_connection.get_channel(idx))

    async def set_channel(self, idx, name, secret):
        return await self.queue.send(lambda: self.meshcore_connection.set_channel(idx, name, secret))

    async def get_channels(self):
        return await self.queue.send(lambda: self.meshcore_connection.get_channels())

    # --- Device / Radio ---
    async def set_radio_params(self, freq, bw, sf, cr):
        return await self.queue.send(lambda: self.meshcore_connection.set_radio_params(freq, bw, sf, cr))

    async def get_device_time(self):
        return await self.queue.send(lambda: self.meshcore_connection.get_device_time())

    async def set_device_time(self, epoch_secs):
        return await self.queue.send(lambda: self.meshcore_connection.set_device_time(epoch_secs))

    async def get_battery_voltage(self):
        return await self.queue.send(lambda: self.meshcore_connection.get_battery_voltage())

    async def reboot(self):
        return await self.queue.send(lambda: self.meshcore_connection.reboot())

    # --- Security ---
    async def export_private_key(self):
        return await self.queue.send(lambda: self.meshcore_connection.export_private_key())

    async def import_private_key(self, privkey):
        return await self.queue.send(lambda: self.meshcore_connection.import_private_key(privkey))

    async def sign_start(self):
        return await self.queue.send(lambda: self.meshcore_connection.sign_start())

    async def sign_data(self, data):
        return await self.queue.send(lambda: self.meshcore_connection.sign_data(data))

    async def sign_finish(self):
        return await self.queue.send(lambda: self.meshcore_connection.sign_finish())
    
    async def want_config_id(self):
        return await self.queue.send(lambda: self.meshtastic_connection.want_config_id())

    # --- Loops ---
    def start_loop(self, label, fn, interval=10000):
        self.queue.start_loop(label, fn, interval)

    def stop_loop(self, label):
        self.queue.stop_loop(label)

    def close(self):
        self.meshcore_connection.close()
        super().close()

    def shutdown(self):
        """Gracefully stop queue, close connection, and cleanup singleton."""
        print("[MeshcoreRequests] Shutting down...")

        if self.queue:
            try:
                self.queue.shutdown()   # delegate to MeshcoreCommandQueue
            except Exception as e:
                print(f"[MeshcoreRequests] Error shutting down queue: {e}")

        try:
            self.close()
        except Exception as e:
            print(f"[MeshcoreRequests] Error closing connection: {e}")

        if MeshcoreRequests.instance is self:
            MeshcoreRequests.instance = None

        print("[MeshcoreRequests] Shutdown complete.")

