"""Мост между движком (фоновый поток) и WebSocket-клиентами (asyncio).

Движок зовёт publish() из своего потока; broadcaster раскладывает событие по
очередям всех подключённых клиентов через call_soon_threadsafe.
"""
from __future__ import annotations

import asyncio
from typing import Optional


class EventBus:
    def __init__(self) -> None:
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._clients: set[asyncio.Queue] = set()

    def bind_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop

    def publish(self, event: dict) -> None:
        """Вызывается из потока движка. Без активного loop — тихо игнорируем."""
        loop = self._loop
        if loop is None:
            return
        for q in list(self._clients):
            loop.call_soon_threadsafe(q.put_nowait, event)

    def register(self) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue()
        self._clients.add(q)
        return q

    def unregister(self, q: asyncio.Queue) -> None:
        self._clients.discard(q)
