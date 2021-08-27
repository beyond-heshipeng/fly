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
from scrapy.utils.display import _tty_supports_color


def _colorize(text, colorize=True):
    if not colorize or not sys.stdout.isatty() or not _tty_supports_color():
        return text
    try:
        from pygments import highlight
    except ImportError:
        return text
    else:
        from pygments.formatters import TerminalFormatter
        from pygments.lexers import PythonLexer
        return highlight(text, PythonLexer(), TerminalFormatter())


def test(obj, *args, **kwargs):
    return _colorize(pformat(obj), kwargs.pop('colorize', True))


print(test({'a': 1}))

