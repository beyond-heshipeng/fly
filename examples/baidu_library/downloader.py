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
        self.browser = None
        self.page = None

    async def open(self):
        self.browser = await launch(headless=self.settings.getboolean("HEADLESS"),
                                    userDataDir=self.settings.get("USER_DATA_DIR", "./cache"),
                                    options={'args': ['--no-sandbox', '--disable-infobars'], 'autoClose': False},
                                    loop=self.spider.loop)

    async def fetch(self, request: Request) -> (Response, Exception):
        page = await self.browser.newPage()
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

    async def close(self):
        await self.browser.close()
