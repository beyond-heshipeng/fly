import asyncio
from typing import AsyncIterable

from fly import Request, Spider
from fly.exceptions import QueueEmptyErr


class Scheduler:
    def __init__(self, loop):
        self.loop = loop
        self.queue = asyncio.PriorityQueue()

    def has_pending_request(self) -> bool:
        return not self.queue.empty()

    async def enqueue_request(self, request: Request) -> None:
        self.loop.call_soon_threadsafe(self.queue.put_nowait, (request.priority, request))

    async def next_request(self) -> Request:
        try:
            _, request = self.queue.get_nowait()
        except asyncio.queues.QueueEmpty:
            raise QueueEmptyErr("scheduler is empty")
        return request

    @classmethod
    async def make_request_from_url(cls, spider: Spider) -> AsyncIterable:
        for url in spider.start_urls:
            yield Request(url, skip_filter=True)

    def start(self):
        pass

