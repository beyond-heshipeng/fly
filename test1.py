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


class Base(type):
    def __new__(mcs, cls_name, bases, cls_dict):
        print(mcs)
        print(cls_name)
        print(bases)
        print(cls_dict)
        if 'start_urls' in cls_dict.keys():
            print(cls_dict.get('start_urls'))
        return super().__new__(mcs, cls_name, bases, cls_dict)


class A(metaclass=Base):
    start_urls = []

    def enqueue_request(self):
        pass


class B(A):
    def test(self):
        self.enqueue_request()


# B()


class father():
    def call_children(self):
        child_method = getattr(self, 'out')
        # 获取子类的out()方法
        child_method()
        # 执行子类的out()方法

    def out(self):
        print("hehe1")


class children(father):
    def out(self):
        print("hehe")


child = children()
child.call_children()
