import asyncio
import random
from typing import TypeVar

import aiohttp
import async_timeout

from fly.http.request import Request
from fly.http.response import Response
from fly.utils.log import Logger

try:
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass


SpiderType = TypeVar("SpiderType", bound="Spider")


class AiohttpDownloader:
    name = 'fly.downloader.AiohttpDownloader'

    def __init__(self, spider: SpiderType):
        self.settings = spider.settings
        self.request_session = aiohttp.ClientSession()
        self.randomize_delay = self.settings.getboolean("RANDOMIZE_DOWNLOAD_DELAY")
        self.delay = self.settings.getint("DOWNLOAD_DELAY", 0)

        self.logger = Logger(self.settings, self.name)

    @property
    def download_delay(self):
        if self.randomize_delay:
            return random.uniform(0.5 * self.delay, 1.5 * self.delay)
        return self.delay

    async def fetch(self, request: Request) -> (Response, Exception):
        if self.delay:
            await asyncio.sleep(self.download_delay)

        timeout = self.settings.getint("DOWNLOAD_TIMEOUT", 60)
        try:
            async with async_timeout.timeout(timeout):
                resp = await self._make_request(request)

            response = Response(
                url=str(resp.url),
                status=resp.status,
                headers=dict(resp.headers),
                body=(await resp.text()).encode(),
                request=request,
            )

            return response, None

        except asyncio.TimeoutError:
            self.logger.error(f"Crawled <{request.method} {request.url}> Connect timeout")
            return None, asyncio.TimeoutError
        except aiohttp.ClientOSError as e:
            self.logger.error(f"Crawled <{request.method} {request.url}> Error: {e}")
            return None, aiohttp.ClientOSError

    async def _make_request(self, request: Request):
        if request.method == 'GET':
            request_func = self.request_session.get(
                request.url, headers=request.headers, data=request.body, ssl=request.ssl
            )

        else:
            request_func = self.request_session.post(
                request.url, headers=request.headers, data=request.body, ssl=request.ssl
            )

        return await request_func

    async def close(self):
        """
        Close the aiohttp session
        :return:
        """
        if not self.request_session.closed:
            await self.request_session.close()
