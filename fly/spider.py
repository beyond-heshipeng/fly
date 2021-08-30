import asyncio
import sys
from asyncio import Semaphore
from types import AsyncGeneratorType
from typing import Optional, AsyncIterable, Callable, Coroutine

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


class Base(type):
    def __init__(cls, cls_name, bases, cls_dict):
        # need some seeds
        super().__init__(cls_name, bases, cls_dict)
        logger = Logger(name='fly')
        if (('start_urls' in cls_dict.keys() and not cls_dict['start_urls'] or 'start_urls' not in cls_dict.keys())
                and 'start_requests' not in cls_dict.keys()):
            logger.warning("no url in the crawling job...")
        # return super().__new__(mcs, cls_name, bases, cls_dict)


class Spider(metaclass=Base):
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

        self.loop = asyncio.get_event_loop()
        self.queue = asyncio.Queue()
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
        self.queue.put_nowait((request.priority, request))

    async def has_pending_requests(self) -> bool:
        return self.queue.empty()

    def _next_request(self) -> Request:
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
        async for request in self.make_request_from_url():
            print(request)
            await self.enqueue_request(request)

        while not self._close_spider:
            try:
                request = self._next_request()
                asyncio.ensure_future(self._handle_request(request, self.semaphore))
            except QueueEmptyErr:
                await asyncio.sleep(0.00001)

    def fly(self):
        self.logger.debug(f"{self.name} started")
        self.logger.debug(f"Overridden settings: {Settings(self.custom_settings)}")

        try:
            asyncio.run(self.middleware_manager.process_spider_start(self))

            self.loop.run_until_complete(self._run())
            self.loop.run_until_complete(self.loop.shutdown_asyncgens())
        except KeyboardInterrupt:
            # asyncio.run(self.middleware_manager.process_spider_stop(self))
            asyncio.run(self._stop())
        finally:
            self.logger.debug(f"Success count: {self._success_count}")
            self.logger.debug(f"Failure count: {self._failed_count}")
            self.logger.debug(f"Total count: {self._success_count + self._failed_count}")
            self.logger.debug(f"Closing {self.name} (finished)")

            # logger.info('Error count: {}'.formast(len(cls.error_urls)))
            # logger.info('Time usage: {}'.format(end_time - start_time))
            # logger.info('Spider finished!')

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
