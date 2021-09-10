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
        browser = await launch(headless=True,
                               handleSIGINT=False,
                               handleSIGTERM=False,
                               handleSIGHUP=False,
                               autoClose=False,
                               devtools=True,
                               userDataDir=self.settings.get("USER_DATA_DIR", "./cache"),
                               options={'args': ['--no-sandbox']})

        page = await browser.newPage()
        try:
            options = {"timeout": self.spider.settings.getint("DOWNLOAD_TIMEOUT") * 1000}
            resp = await page.goto(request.url, options=options)

            await page.evaluate(
                '''() =>{ Object.defineProperties(navigator,{ webdriver:{ get: () => false } }) }''')

            await page.evaluate("""
                 () => {
                     let elements = document.getElementsByClassName("read-all");
                     if (elements && elements.length > 0) {
                        elements[0].click();
                     }
                }
            """)

            content = await page.content()
            print(content)

            # if request.meta.get("javascript"):
            #     print(request.meta["javascript"])
            #     dimensions = await page.evaluate(request.meta["javascript"])
            #     print(dimensions)
            # if request.meta.get("javascript"):
            #     await page.waitForXPath("//div[@id='pageNo-4']//img[starts-with(@data-src, "
            #                             "'https://wkretype.bdimg.com/retype/zoom')]")
                # await page.click("span.read-all")

            response = Response(
                url=str(page.url),
                status=resp.status,
                headers=dict(resp.headers),
                body=(await page.content()).encode(),
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
    #     return await asyncio.ensure_future(self._fetch(request), loop=self.spiders.loop)
