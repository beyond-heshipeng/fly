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


# import asyncio
# from pyppeteer import launch
#
#
# async def main():
#     browser = await launch()
#     page = await browser.newPage()
#     await page.goto('https://wenku.baidu.com')
#     await page.screenshot({'path': 'example.png'})
#     await browser.close()
#
# asyncio.get_event_loop().run_until_complete(main())
#
#
