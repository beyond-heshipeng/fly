"""
An extension to retry failed requests that are potentially caused by temporary
problems such as a connection timeout or HTTP 500 error.
"""
from typing import Union
from asyncio import TimeoutError
from aiohttp import ClientTimeout, ClientOSError, ClientConnectorError, ClientSSLError, ServerTimeoutError
from pyppeteer.errors import PageError, TimeoutError as PyTimeoutError, NetworkError, BrowserError

from fly.http.response import Response
from fly.http.request import Request
from fly.spider import Spider


async def get_retry_request(
    request: Request,
    spider: Spider,
    max_retry_times: int,
    priority_adjust: int,
    reason: Union[str, Exception] = 'unspecified',
):
    """
    return a new request copied from the current request.
    """

    settings = spider.settings
    retry_times = request.meta.get('current_retry_times', 0) + 1
    if retry_times <= max_retry_times:
        if reason:
            spider.logger.info(
                f"Retrying {request} (failed {retry_times} times): {reason}"
            )
        else:
            spider.logger.info(
                f"Retrying {request} (failed {retry_times} times)"
            )
        new_request: Request = request.copy()
        new_request.meta['current_retry_times'] = retry_times
        new_request.skip_filter = True
        if priority_adjust is None:
            priority_adjust = settings.getint('RETRY_PRIORITY_ADJUST')
        new_request.priority = request.priority + priority_adjust

        return new_request
    else:
        if reason:
            spider.logger.error(
                f"Gave up retrying {request} (failed {retry_times} times): {reason}",
            )
        else:
            spider.logger.error(
                f"Gave up retrying {request} (failed {retry_times} times)"
            )
        return None


class RetryMiddleware:
    name = "retry middleware"

    # IOError is raised by the HttpCompression middleware when trying to
    # decompress an empty response
    EXCEPTIONS_TO_RETRY = (
        TimeoutError,
        ConnectionRefusedError,
        IOError,

        ClientTimeout,
        ClientOSError,
        ClientConnectorError,
        ClientSSLError,
        ServerTimeoutError,

        PageError,
        PyTimeoutError,
        NetworkError,
        BrowserError
    )

    def __init__(self, spider: Spider):
        self.enable_retry = spider.settings.getboolean("ENABLE_RETRY", True)
        self.max_retry_times = spider.settings.getint('RETRY_TIMES', 2)
        self.retry_http_codes = set(int(x) for x in spider.settings.getlist('RETRY_HTTP_CODES'))
        self.priority_adjust = spider.settings.getint('RETRY_PRIORITY_ADJUST', -1)

    def adjust_settings(self, request: Request) -> None:
        if "ENABLE_RETRY" in request.meta.keys() and type(request.meta["ENABLE_RETRY"]) is bool:
            self.enable_retry = request.meta["ENABLE_RETRY"]
        if "RETRY_TIMES" in request.meta.keys() and type(request.meta["RETRY_TIMES"]) is int:
            self.max_retry_times = request.meta["RETRY_TIMES"]
        if "RETRY_HTTP_CODES" in request.meta.keys() and type(request.meta["RETRY_HTTP_CODES"]) is list:
            self.retry_http_codes = request.meta["RETRY_HTTP_CODES"]
        if "RETRY_PRIORITY_ADJUST" in request.meta.keys() and type(request.meta["RETRY_PRIORITY_ADJUST"]) is int:
            self.priority_adjust = request.meta["RETRY_PRIORITY_ADJUST"]

    @classmethod
    def from_spider(cls, spider):
        return cls(spider)

    async def process_response(self, request: Request, response: Response, spider: Spider):
        self.adjust_settings(request)

        if not self.enable_retry:
            return response
        if response.status in self.retry_http_codes:
            return await self._retry(request, spider) or response

        return

    async def process_exception(self, request, spider, exception):
        self.adjust_settings(request)

        if not self.enable_retry:
            return

        for e in self.EXCEPTIONS_TO_RETRY:
            if exception == e or isinstance(exception, e):
                return await self._retry(request, spider, exception)

        return

    async def _retry(self, request, spider, exception=None):
        return await get_retry_request(
            request,
            spider=spider,
            reason=exception,
            max_retry_times=self.max_retry_times,
            priority_adjust=self.priority_adjust,
        )
