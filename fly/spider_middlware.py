from fly.middleware import MiddlewareManager
from fly.settings import Settings


class SpiderMiddlewareManager(MiddlewareManager):
    @classmethod
    def _get_middleware_list_from_setting(cls, settings: Settings) -> list:
        pass
