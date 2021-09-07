from inspect import iscoroutinefunction
from typing import TypeVar

from fly.exceptions import InvalidDownloaderErr
from fly.http.request import Request
from fly.http.response import Response
from fly.utils.misc import load_object


SpiderType = TypeVar("SpiderType", bound="Spider")


class DownloaderManager:
    name = 'base downloader'

    def __init__(self, download_obj):
        self.download_obj = download_obj

    async def fetch(self, request: Request) -> (Response, Exception):
        if hasattr(self.download_obj, "fetch"):
            try:
                if iscoroutinefunction(self.download_obj.fetch):
                    return await self.download_obj.fetch(request)
                return self.download_obj.fetch(request)
            except Exception as e:
                raise InvalidDownloaderErr(f"<{repr(self.download_obj)}>: {e}")

    @classmethod
    def from_spider(cls, spider: SpiderType, *args, **kwargs):
        downloader_cls = load_object(spider.settings.get("DOWNLOADER"))
        download_obj = downloader_cls(spider, *args, **kwargs)
        return cls(download_obj)

    async def open(self):
        if hasattr(self.download_obj, "open"):
            try:
                if iscoroutinefunction(self.download_obj.close):
                    await self.download_obj.open()
                    return
                self.download_obj.open()
            except Exception as e:
                raise InvalidDownloaderErr(f"<{repr(self.download_obj)}>: {e}")

    async def close(self):
        if hasattr(self.download_obj, "close"):
            try:
                if iscoroutinefunction(self.download_obj.close):
                    await self.download_obj.close()
                    return
                self.download_obj.close()
            except Exception as e:
                raise InvalidDownloaderErr(f"<{repr(self.download_obj)}>: {e}")
