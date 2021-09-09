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
import nest_asyncio

from aiomultiprocess import Process

from pyppeteer import launch
from pyppeteer.errors import PageError

if sys.version_info >= (3, 8) and sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


is_close = False


async def run():
    global is_close
    while not is_close:
        await asyncio.ensure_future(handle_request("http://wenku.baidu.com"))
        await asyncio.sleep(5)


async def handle_request(url):
    return await fetch(url)


async def fetch(url):
    browser = await launch(headless=False,
                           handleSIGINT=False,
                           handleSIGTERM=False,
                           handleSIGHUP=False,
                           autoClose=False,
                           userDataDir="./examples/baidu_library/cache",
                           options={'args': ['--disable-infobars']})
    page = await browser.newPage()
    try:
        options = {"timeout": 30000}
        resp = await page.goto(url, options=options)
        response = await resp.text()

        return response, None
    except PageError as err:
        print(err)
        return None, PageError
    finally:
        await page.close()
        await browser.close()


def close():
    loop.close()


# nest_asyncio.apply()
loop = asyncio.get_event_loop()
try:
    # asyncio.ensure_future(run(), loop=loop)
    # signal.signal(signal.SIGINT, close)
    # signal.signal(signal.SIGTERM, close)
    # loop.run_forever()
    loop.run_until_complete(run())
    print(222)
except KeyboardInterrupt:
    print(111)
    is_close = True
    if not loop.is_closed():
        loop.stop()
    loop.run_forever()
finally:
    if not loop.is_closed():
        loop.close()
    # if not loop.is_closed():
    #     loop.close()
    # loop.shutdown_asyncgens()
    pass

# loop.run_until_complete(run())
# is_close = True
# loop.close()
