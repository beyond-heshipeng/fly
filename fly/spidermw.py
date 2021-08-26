import weakref
from collections import defaultdict, deque
from inspect import isawaitable
from typing import Deque, Callable, Dict

from fly.exceptions import InvalidMiddlewareErr
from fly.http.request import Request


class MiddlewareManager:
    name = "middleware manager"

    def __init__(self):
        self.methods: Dict[str, Deque[Callable]] = defaultdict(deque)

    def register_middleware(self, *middlewares):
        for mw in middlewares:
            if hasattr(mw, 'process_spider_start'):
                self.methods['process_spider_start'].append(mw.process_spider_start)
            if hasattr(mw, 'process_spider_stop'):
                self.methods['process_spider_stop'].appendleft(mw.process_spider_stop)

            if hasattr(mw, 'process_request'):
                self.methods['process_request'].append(mw.process_request)
            if hasattr(mw, 'process_response'):
                self.methods['process_response'].append(mw.process_response)

    async def process_spider_start(self, spider):
        """ spider middleware, before spider

        :return:
        """
        for mw in self.methods['process_spider_start']:
            if callable(mw):
                try:
                    func = mw(weakref.proxy(self), spider)
                    if isawaitable(func):
                        await func
                except Exception as e:
                    raise InvalidMiddlewareErr(f"<{repr(mw)}>: {e}")

    async def process_spider_stop(self, spider):
        """ spider middleware, after spider

        :return:
        """
        for mw in self.methods['process_spider_finish']:
            if callable(mw):
                try:
                    func = mw(weakref.proxy(self), spider)
                    if isawaitable(func):
                        await func
                except Exception as e:
                    raise InvalidMiddlewareErr(f"<Spider middleware {mw.__name__}>: {e}")

    async def process_request(self, request: Request, spider):
        """ download middleware, before request

        :return:
        """
        for mw in self.methods['process_request']:
            if callable(mw):
                try:
                    func = mw(weakref.proxy(self), request, spider)
                    if isawaitable(func):
                        await func
                except Exception as e:
                    raise InvalidMiddlewareErr(f"<{repr(mw)}>: {e}")

    async def process_response(self, request: Request, spider):
        """ download middleware, after response

        :return:
        """
        for mw in self.methods['process_response']:
            if callable(mw):
                try:
                    func = mw(weakref.proxy(self), request, spider)
                    if isawaitable(func):
                        await func
                except Exception as e:
                    raise InvalidMiddlewareErr(f"<{repr(mw)}>: {e}")

