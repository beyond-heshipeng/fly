import asyncio
import selectors
import sys
import time
from asyncio import Semaphore
from types import AsyncGeneratorType
from typing import Optional, AsyncIterable, Callable, Coroutine
from inspect import isasyncgenfunction, iscoroutinefunction

import aiohttp

from fly.downloader import Downloader
from fly.exceptions import QueueEmptyErr
from fly.settings import Settings
from fly.http.request import Request
from fly.http.response import Response
from fly.middleware import MiddlewareManager
from fly.utils.log import Logger
from fly.utils.settings import get_settings

if sys.version_info >= (3, 8) and sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

if sys.version_info >= (3, 9):
    async_all_tasks = asyncio.all_tasks
    async_current_task = asyncio.current_task
else:
    async_all_tasks = asyncio.Task.all_tasks
    async_current_task = asyncio.tasks.Task.current_task
try:
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass


class Spider:
    name: Optional[str] = None
    start_urls: Optional[list] = []

    allowed_domains: list = []
    allowed_status: list = []

    custom_settings: Optional[dict] = {}

    def __init__(self, name: str = None):
        if name is not None:
            self.name = name
        elif not getattr(self, 'name', None):
            raise ValueError(f"{type(self).__name__} must have a name")
        if not hasattr(self, 'start_urls'):
            self.start_urls = []

        self.settings = get_settings(self.custom_settings)
        self.logger = Logger(self.settings, self.name)

        self.loop = asyncio.SelectorEventLoop(selectors.SelectSelector())
        asyncio.set_event_loop(self.loop)

        self.queue = asyncio.PriorityQueue()
        self.semaphore = asyncio.Semaphore(self.settings.getint("CONCURRENT_REQUESTS"))

        self.session = aiohttp.ClientSession()
        self.downloader = Downloader(self.settings, self.session)

        self.middleware_manager = MiddlewareManager()
        # register spider middleware
        if spider_mws := self.settings.getlist("SPIDER_MIDDLEWARE", []):
            self.middleware_manager.register_middleware(*spider_mws)
        # register download middleware
        if download_mws := self.settings.getlist("DOWNLOAD_MIDDLEWARE", []):
            self.middleware_manager.register_middleware(*download_mws)

        self._close_spider: bool = False
        self._failed_count: int = 0
        self._success_count: int = 0

    async def make_request_from_url(self) -> AsyncIterable:
        for url in self.start_urls:
            yield Request(url, skip_filter=True)

    async def enqueue_request(self, request: Request) -> None:
        # self.queue.put_nowait((request.priority, request))
        self.loop.call_soon_threadsafe(self.queue.put_nowait, (request.priority, request))

    async def has_pending_requests(self) -> bool:
        return self.queue.empty()

    async def _next_request(self) -> Request:
        try:
            _, request = self.queue.get_nowait()
        except asyncio.queues.QueueEmpty:
            raise QueueEmptyErr("scheduler is empty")
        return request

    async def _process_async_callback(self, callback_results: AsyncGeneratorType):
        # AsyncGeneratorType
        async for callback_result in callback_results:
            if isinstance(callback_result, AsyncGeneratorType):
                await self._process_async_callback(callback_result)
            elif isinstance(callback_result, Request):
                if callback_result:
                    await self.enqueue_request(callback_result)
            elif isinstance(callback_result, Coroutine):
                await self._handle_coroutine_callback(callback_result)

    async def _handle_coroutine_callback(self, aws_callback: Coroutine):
        result = await aws_callback
        if result and isinstance(result, Request):
            await self.enqueue_request(result)

    async def _handle_request_callback(self, callback: Callable, response: Response):
        callback_results = callback(response)
        if isinstance(callback_results, AsyncGeneratorType):
            await self._process_async_callback(callback_results=callback_results)
        elif isinstance(callback_results, Coroutine):
            await self._handle_coroutine_callback(callback_results)

    async def _handle_request(self, request: Request, semaphore: Semaphore):
        response = None

        # downloader middleware process request first.
        result = await self.middleware_manager.process_request(request, spider=self)

        if result and isinstance(result, Request):
            request = result
        elif result and isinstance(result, Response):
            response = result

        if not response:
            async with semaphore:
                response = await self.downloader.fetch(request=request)
                if not response:
                    self._failed_count += 1
                    return

                if self.allowed_status and result.status not in self.allowed_status:
                    self._failed_count += 1
                else:
                    self._success_count += 1

        # downloader middleware process response
        result = await self.middleware_manager.process_response(result, spider=self)

        if result and isinstance(result, Request):
            await self.enqueue_request(request)
            return

        if result and isinstance(result, Response):
            response = result

        self.logger.debug(f"Crawled ({response.status}) <{request.method} {request.url}>")

        # call request callback
        if request.callback:
            await self._handle_request_callback(request.callback, response)

    async def _run(self):
        # url from start_urls
        async for request in self.make_request_from_url():
            await self.enqueue_request(request)

        # url from start_requests
        if hasattr(self, "start_requests"):
            start_requests = getattr(self, 'start_requests')
            if callable(start_requests):
                if isasyncgenfunction(start_requests):
                    if isinstance(start_requests(), AsyncIterable):
                        async for request in start_requests():
                            if isinstance(request, Request):
                                await self.enqueue_request(request)
                else:
                    if iscoroutinefunction(start_requests):
                        result = await start_requests()
                    else:
                        result = start_requests()
                    if isinstance(result, Request):
                        await self.enqueue_request(await start_requests())

        while not self._close_spider:
            try:
                request = await self._next_request()
                asyncio.ensure_future(self._handle_request(request, self.semaphore))
            except QueueEmptyErr:
                await asyncio.sleep(0.00001)

    def fly(self):
        self.logger.debug(f"{self.name} started")
        self.logger.debug(f"Overridden settings: {Settings(self.custom_settings)}")
        start = time.time()

        try:
            asyncio.run(self.middleware_manager.process_spider_start(self))

            self.loop.run_until_complete(self._run())
            self.loop.run_until_complete(self.loop.shutdown_asyncgens())
        except KeyboardInterrupt:
            asyncio.run(self.middleware_manager.process_spider_stop(self))
            asyncio.run(self._stop())
        finally:
            end = time.time()

            self.logger.debug(f"Success count: {self._success_count}")
            self.logger.debug(f"Failure count: {self._failed_count}")
            self.logger.debug(f"Total count: {self._success_count + self._failed_count}")
            self.logger.debug(f"Time usage: {end - start}")
            self.logger.debug(f"Closing {self.name} (finished)")

            if not self.loop.is_closed():
                self.loop.close()
            asyncio.run(self.session.close())

    @staticmethod
    async def cancel_all_tasks():
        """
        Cancel all tasks
        :return:

        """
        tasks = []
        for task in async_all_tasks():
            if task is not async_current_task():
                tasks.append(task)
                task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _stop(self):
        """
        Finish all running tasks, cancel remaining tasks.
        :return:
        """
        self.logger.debug(f"Stopping {self.name} ...")
        await self.cancel_all_tasks()
        self.loop.stop()
        self._close_spider = True
