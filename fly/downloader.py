import asyncio
import random

import aiohttp
import async_timeout

from fly.http.request import Request
from fly.http.response import Response
from fly.settings import Settings

try:
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass


class Downloader:
    def __init__(self, settings: Settings, session=None):
        self.settings = settings
        self.request_session = session

        self.concurrency = self.settings.getint("CONCURRENT_REQUESTS")
        self.randomize_delay = self.settings.getboolean("RANDOMIZE_DOWNLOAD_DELAY")
        self.delay = self.settings.getint("DOWNLOAD_DELAY", 0)
        self.close_request_session = False

    @property
    def current_request_session(self):
        if self.request_session is None:
            self.request_session = aiohttp.ClientSession()
            self.close_request_session = True
        return self.request_session

    @property
    def download_delay(self):
        if self.randomize_delay:
            return random.uniform(0.5 * self.delay, 1.5 * self.delay)
        return self.delay

    async def fetch(self, request: Request):
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

            return response

        except asyncio.TimeoutError:
            pass
        except aiohttp.ClientOSError:
            pass
        finally:
            # Close client session
            if self.close_request_session:
                await self._close_session()

    async def _make_request(self, request: Request):
        if request.method == 'GET':
            request_func = self.current_request_session.get(
                request.url, headers=request.headers, data=request.body, ssl=request.ssl, **request.aiohttp_kwargs
            )

        else:
            request_func = self.current_request_session.post(
                request.url, headers=request.headers, data=request.body, ssl=request.ssl, **request.aiohttp_kwargs
            )

        return await request_func

    async def _close_session(self):
        """
        Close the aiohttp session
        :return:
        """
        await self.request_session.close()
