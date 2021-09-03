"""
An extension to retry failed requests that are potentially caused by temporary
problems such as a connection timeout or HTTP 500 error.
"""
from typing import Union
from asyncio import TimeoutError
from aiohttp import ClientTimeout, ClientOSError, ClientConnectorError, ClientSSLError

from fly.http.response import Response
from fly.settings import Settings

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
        spider.logger.debug(
            f"Retrying {request} (failed {retry_times} times): {reason.__name__}"
        )
        new_request: Request = request.copy()
        new_request.meta['current_retry_times'] = retry_times
        new_request.skip_filter = True
        if priority_adjust is None:
            priority_adjust = settings.getint('RETRY_PRIORITY_ADJUST')
        new_request.priority = request.priority + priority_adjust

        return new_request
    else:
        spider.logger.error(
            f"Gave up retrying {request} (failed {retry_times} times): {reason.__name__}",
        )
        return None


class RetryMiddleware:
    # IOError is raised by the HttpCompression middleware when trying to
    # decompress an empty response
    EXCEPTIONS_TO_RETRY = (TimeoutError, ConnectionRefusedError, ClientTimeout, ClientOSError,
                           ClientConnectorError, ClientSSLError, IOError)

    def __init__(self, settings: Settings):
        self.enable_retry = settings.getboolean("ENABLE_RETRY", True)
        self.max_retry_times = settings.getint('RETRY_TIMES', 2)
        self.retry_http_codes = set(int(x) for x in settings.getlist('RETRY_HTTP_CODES'))
        self.priority_adjust = settings.getint('RETRY_PRIORITY_ADJUST', -1)

    def adjust_settings(self, request: Request) -> None:
        if "ENABLE_RETRY" in request.meta.keys() and type( request.meta["ENABLE_RETRY"]) is bool:
            self.enable_retry = request.meta["ENABLE_RETRY"]
        if "RETRY_TIMES" in request.meta.keys() and type(request.meta["RETRY_TIMES"]) is int:
            self.max_retry_times = request.meta["RETRY_TIMES"]
        if "RETRY_HTTP_CODES" in request.meta.keys() and type(request.meta["RETRY_HTTP_CODES"]) is list:
            self.retry_http_codes = request.meta["RETRY_HTTP_CODES"]
        if "RETRY_PRIORITY_ADJUST" in request.meta.keys() and type(request.meta["RETRY_PRIORITY_ADJUST"]) is int:
            self.priority_adjust = request.meta["RETRY_PRIORITY_ADJUST"]

    @classmethod
    def from_settings(cls, settings):
        return cls(settings)

    async def process_response(self, request: Request, response: Response, spider: Spider):
        self.adjust_settings(request)

        if not self.enable_retry:
            return response
        if response.status in self.retry_http_codes:
            return self._retry(request, spider) or response
        return response

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
