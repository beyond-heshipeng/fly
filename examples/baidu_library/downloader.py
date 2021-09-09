import asyncio

from pyppeteer import launch
from pyppeteer.errors import PageError

from fly import Request, Response, Settings

try:
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass


class PyppeteerDownloader:
    def __init__(self, spider):
        self.spider = spider
        self.settings: Settings = spider.settings

    async def fetch(self, request: Request) -> (Response, Exception):
        browser = await launch(headless=self.settings.getboolean("HEADLESS"),
                               handleSIGINT=False,
                               handleSIGTERM=False,
                               handleSIGHUP=False,
                               autoClose=False,
                               userDataDir=self.settings.get("USER_DATA_DIR", "./cache"),
                               options={'args': ['--disable-infobars']})

        page = await browser.newPage()
        try:
            options = {"timeout": self.spider.settings.getint("DOWNLOAD_TIMEOUT") * 1000}
            resp = await page.goto(request.url, options=options)
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
            await page.close()
            await browser.close()

    # async def fetch(self, request: Request) -> (Response, Exception):
    #     return await asyncio.ensure_future(self._fetch(request), loop=self.spider.loop)
