import asyncio

from pyppeteer.launcher import Launcher
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
        pass
        # self.browser = await launch(headless=self.settings.getboolean("HEADLESS"),
        #                             autoClose=False,
        #                             userDataDir=self.settings.get("USER_DATA_DIR", "./cache"),
        #                             options={'args': ['--disable-infobars']},
        #                             loop=self.spider.loop)

    async def fetch(self, request: Request) -> (Response, Exception):
        # self._browser = syncer.sync(pyppeteer.launch())
        # self._page = syncer.sync(self._browser.pages())[0]  # about:blank page
        launch = Launcher(headless=self.settings.getboolean("HEADLESS"),
                          userDataDir=self.settings.get("USER_DATA_DIR", "./cache"),
                          options={'args': ['--no-sandbox', '--disable-infobars'], 'autoClose': False,
                                   'loop': self.spider.loop},
                          loop=self.spider.loop)
        browser = await launch.launch()
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
            # self.spider.loop.run_until_complete(launch.killChrome())
            # await launch.killChrome()
            launch.waitForChromeToClose()
            # await browser.close()

    async def close(self):
        pass
        # await self.browser.close()
