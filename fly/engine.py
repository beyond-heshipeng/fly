import asyncio
from inspect import isasyncgenfunction, iscoroutinefunction
from typing import AsyncIterable

from fly import Spider, Logger, Request
from fly.exceptions import QueueEmptyErr
from fly.scheduler import Scheduler
from fly.middleware import MiddlewareManager
from fly.const import EngineStatus, SpiderStatus
from fly.utils import get_project_settings


class Engine:
    name = 'fly.engine'

    def __init__(
        self,
        scheduler: Scheduler = None,
    ):
        self._status_lock = asyncio.Lock()
        self._spiders_status = {}

        self.logger = Logger(get_project_settings(), self.name)

        self._scheduler = scheduler or Scheduler()
        self._middleware_manager = MiddlewareManager()

        self._status = EngineStatus.ENGINE_STATUS_STOPPED

        self._total_failed_count: int = 0
        self._total_success_count: int = 0

    async def start(self):
        if self._status != EngineStatus.ENGINE_STATUS_STOPPED:
            return

        self.logger.debug(f"{self.name} started")

        # 启动调度器
        await self._scheduler.start()

        try:
            request = await asyncio.wait_for(self._scheduler.next_request(), 5)
            asyncio.ensure_future(self._handle_request(request, self.semaphore))
        except QueueEmptyErr:
            await asyncio.sleep(0.00001)

    async def _add_spider(self, spider: Spider):
        with self._status_lock:
            self._spiders_status[spider.name].status = SpiderStatus.SPIDER_STATUS_RUNNING

        # url from start_urls
        async for request in self._scheduler.make_request_from_url(spider):
            await self._scheduler.enqueue_request(request)

        # url from start_requests
        if hasattr(self, "start_requests"):
            start_requests = getattr(self, 'start_requests')
            if callable(start_requests):
                if isasyncgenfunction(start_requests):
                    if isinstance(start_requests(), AsyncIterable):
                        async for request in start_requests():
                            if isinstance(request, Request):
                                await self._scheduler.enqueue_request(request)
                else:
                    if iscoroutinefunction(start_requests):
                        result = await start_requests()
                    else:
                        result = start_requests()
                    if isinstance(result, Request):
                        await self._scheduler.enqueue_request(await start_requests())

    def _run_spider(self, spider: Spider):
        with self._status_lock:
            self._spiders_status[spider.name].status = SpiderStatus.SPIDER_STATUS_RUNNING

    def _stop_spider(self, spider: Spider):
        with self._status_lock:
            self._spiders_status[spider.name].status = SpiderStatus.SPIDER_STATUS_STOPPED

    def _del_spider(self, spider: Spider):
        with self._status_lock:
            self._spiders_status[spider.name].status = SpiderStatus.SPIDER_STATUS_DELETED
