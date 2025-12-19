# src/meshtastic/utils/meshcore_command_queue.py

import asyncio
import time
import inspect
from typing import Callable, Dict, Optional, Any
from asyncio import get_running_loop


class CommandQueue:
    def __init__(self, on_fn, timeout_ms: int = 5000):
        self.timeout_ms = timeout_ms
        self.queue: list[Callable[[], Any]] = []
        self.waiting: Optional[Callable[[str], None]] = None
        self.is_processing = False
        self.loops: Dict[str, asyncio.Task] = {}

        # Bind handler events
        on = on_fn
        on("ok", lambda _: self._resolve_waiting("ok"))
        on("err", lambda _: self._resolve_waiting("err"))

    def _resolve_waiting(self, status: str):
        if self.waiting:
            self.waiting(status)

    async def send(self, command_fn: Callable) -> str:
        """
        Enqueue a command function and wait for its result.
        Returns 'ok', 'err', 'timeout', or 'error'.
        """
        loop = get_running_loop()

        fut = loop.create_future()

        async def task():
            start_time = time.time()

            timer = loop.call_later(
                self.timeout_ms / 1000,
                lambda: self._timeout(command_fn, fut, start_time)
            )

            def waiting(status: str):
                timer.cancel()
                duration = int((time.time() - start_time) * 1000)
                if not fut.done():
                    fut.set_result(status)
                self.waiting = None
                self.process_next()

            self.waiting = waiting

            try:
                result = command_fn()
                if inspect.isawaitable(result):
                    await result
                else:
                    print("[CommandQueue] Result not awaitable; treating as sync.")
                # Fallback: if no event resolved yet, mark ok
                if self.waiting:
                    self.waiting("ok")
            except Exception as err:
                timer.cancel()
                print(f"[CommandQueue] Command dispatch error: {err!r}")
                if self.waiting:
                    self.waiting("error")

        self.queue.append(task)

        if not self.is_processing and not self.waiting:
            self.process_next()

        return await fut

    def _timeout(self, ref, fut, start_time):
        if self.waiting:
            self.waiting("timeout")

    def process_next(self):
        if self.queue:
            self.is_processing = True
            next_task = self.queue.pop(0)
            asyncio.create_task(next_task())
        else:
            self.is_processing = False

    def flush(self):
        self.queue.clear()
        self.waiting = None
        self.is_processing = False

    def is_idle(self) -> bool:
        idle = len(self.queue) == 0 and self.waiting is None
        return idle

    def start_loop(self, label: str, command_fn: Callable[[], asyncio.Future], interval_ms: int = 3600000):
        if label in self.loops:
            return self.loops[label]

        async def loop_fn():
            while True:
                try:
                    result = await command_fn()
                except Exception as err:
                    print(f"[CommandQueue] Loop '{label}' error: {err!r}")
                await asyncio.sleep(interval_ms / 1000)

        task = asyncio.create_task(loop_fn())
        self.loops[label] = task
        return task

    def stop_loop(self, label: str):
        task = self.loops.get(label)
        if task:
            task.cancel()
            del self.loops[label]

    async def await_connected(self, emitter, timeout_ms: int = 5000):
        """
        Wait until emitter fires 'connected' or timeout.
        """
        loop = get_running_loop()
        fut = loop.create_future()

        def on_connected(info):
            if not fut.done():
                fut.set_result(info)

        def on_error(err):
            print(f"[CommandQueue] await_connected got 'error' err={err!r}")
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

    # --- Shutdown ---
    def shutdown(self):
        """Gracefully stop all loops, flush queue, and reset state."""
        print("[CommandQueue] Shutting down...")

        # Cancel all active loops
        for label, task in list(self.loops.items()):
            try:
                task.cancel()
                print(f"[CommandQueue] Loop '{label}' cancelled.")
            except Exception as e:
                print(f"[CommandQueue] Error cancelling loop '{label}': {e}")
            finally:
                del self.loops[label]

        # Clear any queued commands
        self.flush()

        print("[CommandQueue] Shutdown complete.")
