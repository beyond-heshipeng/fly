import asyncio
import sys
import time
from asyncio import Semaphore, CancelledError
from types import AsyncGeneratorType
from typing import Optional, AsyncIterable, Callable, Coroutine, final
from inspect import isasyncgenfunction, iscoroutinefunction

from aiomultiprocess import Worker, Pool

from fly.utils.log import Logger
from fly.downloader import DownloaderManager
from fly.exceptions import QueueEmptyErr
from fly.settings import Settings
from fly.http.request import Request
from fly.http.response import Response
from fly.download_middlewares import DownloadMiddlewareManager
from fly.utils.settings import get_settings

if sys.version_info >= (3, 8) and sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

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


class Spider(object):
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

        if hasattr(self, "custom_settings"):
            custom_settings = getattr(self, "custom_settings")
        else:
            custom_settings = self.custom_settings
        self.settings = get_settings(custom_settings)

        self.logger = Logger(self.settings, self.name)

        self.semaphore = asyncio.Semaphore(self.settings.getint("CONCURRENT_REQUESTS"))

        self.loop = asyncio.get_event_loop()
        self.queue = asyncio.PriorityQueue()

        self.downloader_manager = DownloaderManager.from_spider(self)
        self.downloader_middleware = DownloadMiddlewareManager.from_spider(self)

        self._close_spider: bool = False
        self._failed_count: int = 0
        self._success_count: int = 0

    async def make_request_from_url(self) -> AsyncIterable:
        for url in self.start_urls:
            yield Request(url, skip_filter=True)

    async def enqueue_request(self, request: Request) -> None:
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
        result = await self.downloader_middleware.process_request(request, spider=self)

        if result and isinstance(result, Request):
            request = result
        elif result and isinstance(result, Response):
            response = result

        if not response:
            async with semaphore:
                start = time.time()
                try:
                    response, exception = await self.downloader_manager.fetch(request=request)
                except Exception as err:
                    exception = err
                    self.logger.error(err)

                if not response:
                    self._failed_count += 1
                    result = await self.downloader_middleware.process_exception(
                        request, exception=exception, spider=self
                    )

                    if not result:
                        return

                else:
                    if self.allowed_status and result.status not in self.allowed_status:
                        self._failed_count += 1
                    else:
                        self._success_count += 1

                    # downloader middleware process response
                    result = await self.downloader_middleware.process_response(
                        request, response, spider=self
                    )
        else:
            # downloader middleware process response
            result = await self.downloader_middleware.process_response(
                request, response, spider=self
            )

        if result and isinstance(result, Request):
            await self.enqueue_request(result)
            return

        if result and isinstance(result, Response):
            response = result

        end = time.time()

        self.logger.info(f"Crawled ({response.status}) <{request.method}"
                         f" {request.url}, cost {end - start}s>")

        # call request callback
        if request.callback:
            await self._handle_request_callback(request.callback, response)

    async def schedule_request(self):
        while not self._close_spider:
            try:
                request = await asyncio.wait_for(self._next_request(), 5)
                asyncio.ensure_future(self._handle_request(request, self.semaphore))
            except QueueEmptyErr:
                await asyncio.sleep(0.00001)

    async def _init_request(self):
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

    async def _run(self):
        # asyncio.run(self.middleware_manager.process_spider_start(self))
        await self.downloader_manager.open()

        await self._init_request()

        async with Pool() as pool:
            async for _ in pool.map(self.schedule_request, ["1"]):
                pass

        # import threading
        # t = threading.Thread(target=self.schedule_request)
        # t.start()
        # t.join()
        # await Worker(
        #     target=self.schedule_request,
        # )

    @final
    def fly(self):
        self.logger.info(f"{self.name} started")
        self.logger.info(f"Overridden settings: {Settings(self.custom_settings)}")

        try:
            self.loop.run_until_complete(self._run())
        except KeyboardInterrupt:
            # asyncio.run(self.middleware_manager.process_spider_stop(self))
            asyncio.run(self._stop())
            self.loop.run_forever()
        finally:

            self.logger.info(f"Success count: {self._success_count}")
            self.logger.info(f"Failure count: {self._failed_count}")
            self.logger.info(f"Total count: {self._success_count + self._failed_count}")
            self.logger.info(f"Closing {self.name} (finished)")

            if not self.loop.is_closed():
                self.loop.close()

    async def cancel_all_tasks(self):
        """
        Cancel all tasks
        :return:

        """
        try:
            tasks = []
            for task in async_all_tasks():
                if task is not async_current_task():
                    tasks.append(task)
                    task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
        except CancelledError as err:
            self.logger.error(err)

    async def _stop(self):
        """
        Finish all running tasks, cancel remaining tasks.
        :return:
        """
        self.loop = asyncio.new_event_loop()
        self.logger.info(f"Stopping {self.name} ...")
        await self.downloader_manager.close()
        self._close_spider = True
        await self.cancel_all_tasks()
        if not self.loop.is_closed():
            self.loop.stop()
