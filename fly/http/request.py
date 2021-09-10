from typing import TypeVar, Optional, Callable, Union
from w3lib.url import safe_url_string

from fly.exceptions import InvalidRequestMethodErr
from fly.http.headers import Headers
from fly.utils.curl import curl_to_request_kwargs
from fly.utils.python import to_bytes
from fly.utils.url import escape_ajax


RequestType = TypeVar("RequestType", bound="Request")


class Request(object):
    """Represents an HTTP request, which is usually generated in a Spider and
    executed by the Downloader, thus generating a :class:`Response`.
    """

    __slot__ = (
        "url",
        "method",
        "headers",
        "body",
        "cookies",
        "meta",
        "encoding",
        "priority",
        "skip_filter",
        "callback",
        "error_back",
        "ssl",
        "aiohttp_kwargs"
    )

    METHOD = ["GET", "POST"]

    def __init__(
        self,
        url: str,
        method: str = "GET",
        headers: dict = None,
        body: Optional[Union[bytes, str]] = None,
        cookies: dict = None,
        meta: dict = None,
        priority: int = 0,
        encoding: str = None,
        skip_filter: bool = False,
        callback: Optional[Callable] = None,
        error_back: Optional[Callable] = None,
        **aiohttp_kwargs,
    ) -> None:
        self.encoding = encoding
        self.method = str(method).upper()
        if self.method not in self.METHOD:
            raise InvalidRequestMethodErr(f"{self.method} method is not supported")

        self.ssl = aiohttp_kwargs.pop("ssl", False)
        self.aiohttp_kwargs = aiohttp_kwargs

        self._set_url(url)
        self._set_body(body)
        self.body = b"" if body is None else to_bytes(body, self.encoding)
        if not isinstance(priority, int):
            raise TypeError(f"Request priority not an integer: {priority!r}")
        self.priority = priority

        if callback is not None and not callable(callback):
            raise TypeError(f'callback must be a callable, got {type(callback).__name__}')
        if error_back is not None and not callable(error_back):
            raise TypeError(f'error_back must be a callable, got {type(error_back).__name__}')
        self.callback = callback
        self.error_back = error_back

        self.cookies = cookies or {}
        self.headers = Headers(headers or {})
        self.skip_filter = skip_filter

        self._set_meta(meta)

    def _set_meta(self, meta):
        if meta is None:
            self.meta = {}
            return

        if type(meta) is not dict:
            raise TypeError(f"meta must be a dict, got {type(meta).__name__}")
        self.meta = dict(meta)

    def _set_url(self, url: str) -> None:
        if not isinstance(url, str):
            raise TypeError(f"Request url must be str, got {type(url).__name__}")

        s = safe_url_string(url, self.encoding)
        self.url = escape_ajax(s)

        if (
                '://' not in self.url
                and not self.url.startswith('about:')
                and not self.url.startswith('data:')
        ):
            raise ValueError(f'Missing scheme in request url: {self.url}')

    def _set_body(self, body) -> None:
        self.body = b"" if body is None else to_bytes(body, self.encoding)

    def __str__(self) -> str:
        return f"<{self.method} {self.url}>"

    __repr__ = __str__

    def copy(self):
        return self.replace()

    def replace(self, *args, **kwargs) -> RequestType:
        """Create a new Request with the same attributes except for those given new values"""
        for x in self.__slot__:
            kwargs.setdefault(x, getattr(self, x))
        cls = kwargs.pop('cls', self.__class__)
        return cls(*args, **kwargs)

    @classmethod
    def from_curl(cls, curl_command: str, ignore_unknown_options: bool = True, **kwargs):
        """Create a Request object from a string containing a `cURL` command.

        """
        request_kwargs = curl_to_request_kwargs(curl_command, ignore_unknown_options)
        request_kwargs.update(kwargs)
        return cls(**request_kwargs)

    def __lt__(self, other):
        return self.priority < other.priority
