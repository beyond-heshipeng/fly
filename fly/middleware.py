import logging

from collections import defaultdict, deque
from inspect import isawaitable
from typing import Dict, Callable, Deque

from fly.exceptions import InvalidDownloadMiddlewareErr
from fly.http.request import Request
from fly.http.response import Response


class Middleware:
    def __init__(self):
        self.methods: Dict[str, Deque[Callable]] = defaultdict(deque)

    def register_middleware(self, *middlewares):
        for mw in middlewares:
            if hasattr(mw, 'process_request'):
                self.methods['process_request'].append(mw.process_request)
            if hasattr(mw, 'process_response'):
                self.methods['process_response'].appendleft(mw.process_response)
            if hasattr(mw, 'process_exception'):
                self.methods['process_exception'].appendleft(mw.process_exception)


    # # async def download(self, download_func: Callable, request: Request, spider: Spider):
    # async def process_request(self, download_func: Callable, request: Request) -> Response:
    #     for method in self.methods['process_request']:
    #         if callable(method):
    #             middleware_func = method(request=request)
    #             try:
    #                 if isawaitable(middleware_func):
    #                     response = await middleware_func
    #
    #                     if response is not None and not isinstance(response, (Response, Request)):
    #                         raise _InvalidOutput(
    #                             f"Middleware {method.__qualname__} must return None, Response or "
    #                             f"Request, got {response.__class__.__name__}"
    #                         )
    #                     if response:
    #                         yield response
    #
    #                 else:
    #                     raise InvalidMiddleware(f"<Middleware {middleware_func.__name__}: must be a coroutine function")
    #             except Exception as e:
    #                 logging.error(f"<Middleware {middleware_func.__name__}: {e}")
    #
    #     return (yield download_func(request=request, spider=spider))