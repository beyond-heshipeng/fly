# import asyncio
#
# import time
#
# now = lambda: time.time()
#
#
# async def do_some_work(x):
#     async with semaphore:
#         print('Waiting: ', x)
#
#         await asyncio.sleep(x)
#     return 'Done after {}s'.format(x)
#
# start = now()
#
# coroutine1 = do_some_work(1)
# coroutine2 = do_some_work(2)
# coroutine3 = do_some_work(3)
# coroutine4 = do_some_work(4)
# coroutine5 = do_some_work(5)
#
# tasks = [
#     asyncio.ensure_future(coroutine1),
#     asyncio.ensure_future(coroutine2),
#     asyncio.ensure_future(coroutine3),
#     asyncio.ensure_future(coroutine4),
#     asyncio.ensure_future(coroutine5),
# ]
#
# semaphore = asyncio.Semaphore(5)
# loop = asyncio.get_event_loop()
# loop.run_until_complete(asyncio.wait(tasks))
#
# for task in tasks:
#     print('Task ret: ', task.result())
#
# print('TIME: ', now() - start)
# import json
import re
import signal
import sys
from pprint import pformat
# ds = [{'hello': 'there'}]
# logging.debug(pformat(ds))
# print(json.dumps([{'hello': 'there'}, {"111": 222}], indent=4))

# import requests
#
# resp = requests.get('http://10.39.203.95:8050/render.html',
#                     params={'url': 'https://36kr.com/search/articles/%E9%98%BF%E9%87%8C%E5%B7%B4%E5%B7%B4', 'wait': 25})
# print(resp.text)


import asyncio

import requests
from lxml import html
from pyppeteer import launch
from pyppeteer.errors import PageError

if sys.version_info >= (3, 8) and sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


pic_count = 0


async def fetch(url):
    browser = await launch(headless=False,
                           userDataDir="./examples/baidu_library/cache")
    page = await browser.newPage()
    try:

        options = {"timeout": 60000}
        await page.goto(url, options=options)
        await page.evaluate(
            '''() =>{ Object.defineProperties(navigator,{ webdriver:{ get: () => false } }) }''')

        await page.evaluate("""
             () => {
                 let elements = document.getElementsByClassName("read-all");
                 if (elements && elements.length > 0) {
                    elements[0].click();
                    window.scrollTo(0, 5000);
                 }
            }
        """)

        response = await page.content()
        # print(response)
        # await asyncio.sleep(60)

        return response
    except PageError as err:
        print(err)
        return None, PageError
    finally:
        await page.close()
        await browser.close()


# nest_asyncio.apply()
if __name__ == '__main__':
    start_requests = [
        "https://wenku.baidu.com/search?word=智慧能源ppt"
        "&lm=0&od=0&fr=top_home&ie=utf-8&pn=1",
        "https://wenku.baidu.com/search?word=智慧能源ppt"
        "&lm=0&od=0&fr=top_home&ie=utf-8&pn=2",
        "https://wenku.baidu.com/search?word=智慧能源ppt"
        "&lm=0&od=0&fr=top_home&ie=utf-8&pn=3"
    ]

    url = "http://110.40.183.167:8000/ocr/ppt_ocr"

    async def parse_detail(response):
        tree = html.fromstring(response)
        title = tree.xpath("//h3[@class='doc-title']//text()")
        images = []
        images.extend(tree.xpath("//img[starts-with(@src, 'https://wkretype.bdimg.com/retype/zoom')]/@src"))
        images.extend(tree.xpath("//img[starts-with(@data-src, 'https://wkretype.bdimg.com/retype/zoom')]/@data-src"))
        summary = "".join(tree.xpath("//div[@class='doc-summary-wrap']//text()"))
        time = re.findall(r"[0-9]{4}-[0-9]{1,2}-[0-9]{1,2}", summary)

        for image in images:
            body = {
                "doc_title": title[0],
                "image": image,
                "image_time": time[0]
            }
            print(body)

            global pic_count
            with open(f"images/{pic_count}.jpg", "wb") as f:
                f.write(requests.get(image).content)
            pic_count += 1
            # resp = requests.post(url, json=body, headers={"Content-Type": "application/json"})
            # print(resp.status_code, resp.text)

    async def run():
        for url in start_requests:
            resp = await fetch(url)
            # print(resp)

            tree = html.fromstring(resp)
            items = tree.xpath("//div[@class='search-result-wrap']")

            for item in items:
                if item.xpath(".//div[@class='doc-icon doc-icon-ppt']"):
                    url = item.xpath(".//a[@class='search-result-title']/@href")
                    if url:
                        print(url[0])
                        await parse_detail(await fetch(url[0]))

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
