import asyncio
import json
from collections import defaultdict


class SSEBroker:
    def __init__(self) -> None:
        self._listeners: dict[int, set[asyncio.Queue[str]]] = defaultdict(set)

    async def subscribe(self, tenant_id: int):
        queue: asyncio.Queue[str] = asyncio.Queue(maxsize=100)
        self._listeners[tenant_id].add(queue)
        try:
            while True:
                payload = await queue.get()
                yield f"event: message\ndata: {payload}\n\n"
        finally:
            self._listeners[tenant_id].discard(queue)

    def publish(self, tenant_id: int, event: dict) -> None:
        payload = json.dumps(event, default=str)
        for queue in list(self._listeners[tenant_id]):
            if queue.full():
                _ = queue.get_nowait()
            queue.put_nowait(payload)


sse_broker = SSEBroker()
