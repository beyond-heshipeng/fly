from collections import defaultdict, deque
from typing import Deque, Callable, Dict
from fly.settings import Settings
from fly.utils.misc import load_object, create_instance


class MiddlewareManager:
    name = "middleware manager"

    def __init__(self, *middlewares):
        self.methods: Dict[str, Deque[Callable]] = defaultdict(deque)
        for mw in middlewares:
            self._register_middleware(mw)

    def _register_middleware(self, middleware) -> None:
        if hasattr(middleware, 'process_spider_start'):
            self.methods['process_spider_start'].append(middleware.process_spider_start)
        if hasattr(middleware, 'process_spider_stop'):
            self.methods['process_spider_stop'].appendleft(middleware.process_spider_stop)

    @classmethod
    def _get_middleware_list_from_setting(cls, settings: Settings) -> list:
        raise NotImplementedError

    @classmethod
    def from_settings(cls, settings: Settings):
        middleware_list = cls._get_middleware_list_from_setting(settings)
        middlewares = []
        for middleware in middleware_list:
            middleware_cls = load_object(middleware)
            mw = create_instance(middleware_cls, settings)
            middlewares.append(mw)
        return cls(*middlewares)
