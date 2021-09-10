import weakref
from inspect import isawaitable, iscoroutinefunction

from fly.exceptions import InvalidMiddlewareErr
from fly.http.request import Request
from fly.http.response import Response
from fly.middleware import MiddlewareManager
from fly.settings import Settings
from fly.utils.components import build_component_list


class DownloadMiddlewareManager(MiddlewareManager):
    name = "download middleware manager"

    @classmethod
    def _get_middleware_list_from_setting(cls, settings: Settings) -> list:
        return build_component_list(settings.get_dict('DOWNLOADER_MIDDLEWARES'))

    def _register_middleware(self, middleware):
        # if hasattr(mw, 'process_spider_start'):
        #     self.methods['process_spider_start'].append(mw.process_spider_start)
        # if hasattr(mw, 'process_spider_stop'):
        #     self.methods['process_spider_stop'].appendleft(mw.process_spider_stop)

        if hasattr(middleware, 'process_request'):
            self.methods['process_request'].append(middleware.process_request)
        if hasattr(middleware, 'process_response'):
            self.methods['process_response'].append(middleware.process_response)
        if hasattr(middleware, 'process_exception'):
            self.methods['process_exception'].appendleft(middleware.process_exception)

    async def process_spider_start(self, spider):
        """ spiders middleware, before spiders

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
        """ spiders middleware, after spiders

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
                    if iscoroutinefunction(mw):
                        return await mw(request, spider)
                    return mw(request, spider)
                except Exception as e:
                    raise InvalidMiddlewareErr(f"<{repr(mw)}>: {e}")

    async def process_response(self, request: Request, response: Response, spider):
        """ download middleware, after response

        :return:
        """
        for mw in self.methods['process_response']:
            if callable(mw):
                try:
                    if iscoroutinefunction(mw):
                        return await mw(request, response, spider)
                    return mw(request, response, spider)
                except Exception as e:
                    raise InvalidMiddlewareErr(f"<{repr(mw)}>: {e}")

    async def process_exception(self, request: Request, exception: Exception, spider):
        """ download middleware, called when exception happens

        :return:
        """
        for mw in self.methods['process_exception']:
            if callable(mw):
                try:
                    if iscoroutinefunction(mw):
                        return await mw(request=request, exception=exception, spider=spider)
                    return mw(request=request, exception=exception, spider=spider)
                except Exception as e:
                    raise InvalidMiddlewareErr(f"<{repr(mw)}>: {e}")
