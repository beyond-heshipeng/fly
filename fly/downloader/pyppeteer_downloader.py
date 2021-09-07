import asyncio

from pyppeteer import launch
from pyppeteer.errors import PageError

from fly.http.request import Request
from fly.http.response import Response

try:
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass


class PyppeteerDownloader:
    def __init__(self, spider):
        self.spider = spider
        self.browser = None
        self.page = None

    async def open(self):
        self.browser = await launch(headless=False)
        self.page = await self.browser.newPage()

    async def fetch(self, request: Request) -> (Response, Exception):
        try:
            options = {"timeout": self.spider.settings.getint("DOWNLOAD_TIMEOUT")}
            resp = await self.page.goto(request.url, options=options)
            response = Response(
                url=str(resp.url),
                status=resp.status,
                headers=dict(resp.headers),
                body=(await resp.text()).encode(),
                request=request,
            )

            return response, None
        except PageError as err:
            self.spider.logger.debug(err)
            return None, PageError
        finally:
            self.page.close()

    async def close(self):
        await self.browser.close()
