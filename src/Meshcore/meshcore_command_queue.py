# src/meshtastic/utils/meshcore_command_queue.py
import asyncio
import time
from typing import Callable, Dict, Optional

class MeshcoreCommandQueue:
    def __init__(self, handler, timeout_ms: int = 5000):
        self.timeout_ms = timeout_ms
        self.queue = []
        self.waiting: Optional[Callable[[str], None]] = None
        self.is_processing = False
        self.loops: Dict[str, asyncio.Task] = {}

        # Bind handler events
        handler.on("ok", lambda: self._resolve_waiting("ok"))
        handler.on("err", lambda: self._resolve_waiting("err"))

    def _resolve_waiting(self, status: str):
        if self.waiting:
            self.waiting(status)

    async def send(self, command_fn: Callable[[], None]) -> str:
        """
        Enqueue a command function and wait for its result.
        Returns 'ok', 'err', 'timeout', or 'error'.
        """
        loop = asyncio.get_event_loop()
        fut = loop.create_future()

        def task():
            start_time = time.time()
            print(f"[MeshcoreQueue] Dispatching command at {time.strftime('%Y-%m-%d %H:%M:%S')}", command_fn)

            timer = loop.call_later(self.timeout_ms / 1000, lambda: self._timeout(command_fn, fut, start_time))

            def waiting(status: str):
                timer.cancel()
                duration = int((time.time() - start_time) * 1000)
                print(f"[MeshcoreQueue] Command result: {status} ({duration}ms)")
                if not fut.done():
                    fut.set_result(status)
                self.waiting = None
                self.process_next()

            self.waiting = waiting

            try:
                command_fn()
            except Exception as err:
                timer.cancel()
                print(f"[MeshcoreQueue] Command dispatch error: {err}")
                if self.waiting:
                    self.waiting("error")

        self.queue.append(task)

        if not self.is_processing and not self.waiting:
            self.process_next()

        return await fut

    def _timeout(self, command_fn, fut, start_time):
        if self.waiting:
            print(f"[MeshcoreQueue] Command timed out after {self.timeout_ms}ms", command_fn)
            self.waiting("timeout")

    def process_next(self):
        if self.queue:
            self.is_processing = True
            next_task = self.queue.pop(0)
            next_task()
        else:
            self.is_processing = False

    def flush(self):
        print("[MeshcoreQueue] Flushing queue — cancelling all pending commands")
        self.queue.clear()
        self.waiting = None
        self.is_processing = False

    def is_idle(self) -> bool:
        return len(self.queue) == 0 and self.waiting is None

    def start_loop(self, label: str, command_fn: Callable[[], asyncio.Future], interval_ms: int = 3600000):
        if label in self.loops:
            print(f"[MeshcoreQueue] Loop '{label}' already running")
            return self.loops[label]

        async def loop_fn():
            while True:
                try:
                    result = await command_fn()
                    print("start loop command", command_fn)
                    if result == "ok":
                        print(f"[MeshcoreQueue] Loop '{label}' command succeeded")
                    elif result == "failed":
                        print(f"[MeshcoreQueue] Loop '{label}' command returned 'failed'")
                    elif result == "timeout":
                        print(f"[MeshcoreQueue] Loop '{label}' command timed out")
                    elif result == "error":
                        print(f"[MeshcoreQueue] Loop '{label}' command threw an error")
                    else:
                        print(f"[MeshcoreQueue] Loop '{label}' returned unknown status: {result}")
                except Exception as err:
                    print(f"[MeshcoreQueue] Loop '{label}' error: {err}")
                await asyncio.sleep(interval_ms / 1000)

        task = asyncio.create_task(loop_fn())
        self.loops[label] = task
        return task

    def stop_loop(self, label: str):
        task = self.loops.get(label)
        if task:
            task.cancel()
            del self.loops[label]
            print(f"[MeshcoreQueue] Loop '{label}' stopped")

    async def await_connected(self, emitter, timeout_ms: int = 5000):
        """
        Wait until emitter fires 'connected' or timeout.
        """
        loop = asyncio.get_event_loop()
        fut = loop.create_future()

        def on_connected(info):
            if not fut.done():
                fut.set_result(info)

        def on_error(err):
            if not fut.done():
                fut.set_exception(err)

        emitter.on("connected", on_connected)
        emitter.once("error", on_error)

        try:
            return await asyncio.wait_for(fut, timeout_ms / 1000)
        except asyncio.TimeoutError:
            raise TimeoutError(f"connected timeout after {timeout_ms}ms")
        finally:
            emitter.off("connected", on_connected)
