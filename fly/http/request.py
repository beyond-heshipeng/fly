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

    __slots__ = (
        "_url",
        "_method",
        "_headers",
        "_body",
        "_cookies",
        "_meta",
        "_encoding",
        "_priority",
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
        self._encoding = encoding
        self._method = str(method).upper()
        if self._method not in self.METHOD:
            raise InvalidRequestMethodErr(f"{self.method} method is not supported")

        self.ssl = aiohttp_kwargs.pop("ssl", False)
        self.aiohttp_kwargs = aiohttp_kwargs

        self._url = url
        self._set_url(url)
        self._body = b"" if body is None else to_bytes(body, self._encoding)
        if not isinstance(priority, int):
            raise TypeError(f"Request priority not an integer: {priority!r}")
        self._priority = priority

        if callback is not None and not callable(callback):
            raise TypeError(f'callback must be a callable, got {type(callback).__name__}')
        if error_back is not None and not callable(error_back):
            raise TypeError(f'error_back must be a callable, got {type(error_back).__name__}')
        self.callback = callback
        self.error_back = error_back

        self._cookies = cookies or {}
        self._headers = Headers(headers or {})
        self.skip_filter = skip_filter

        self._meta = dict(meta) if meta else None

    @property
    def meta(self) -> dict:
        if self._meta is None:
            self._meta = {}
        return self._meta

    @meta.setter
    def meta(self, meta: dict):
        if type(meta) is not dict:
            raise TypeError(f"meta must be a dict, got {type(meta).__name__}")
        self._meta = meta

    @property
    def priority(self):
        return self._priority

    @property
    def url(self) -> str:
        return self._url

    @property
    def method(self) -> str:
        return self._method

    @property
    def headers(self):
        return self._headers

    def _set_url(self, url: str) -> None:
        if not isinstance(url, str):
            raise TypeError(f"Request url must be str, got {type(url).__name__}")

        s = safe_url_string(url, self._encoding)
        self._url = escape_ajax(s)

        if (
            '://' not in self._url
            and not self._url.startswith('about:')
            and not self._url.startswith('data:')
        ):
            raise ValueError(f'Missing scheme in request url: {self._url}')

    @property
    def body(self) -> bytes:
        return self._body

    @body.setter
    def body(self, body) -> None:
        self._body = b"" if body is None else to_bytes(body, self.encoding)

    @property
    def encoding(self) -> str:
        return self._encoding

    def __str__(self) -> str:
        return f"<{self.method} {self.url}>"

    __repr__ = __str__

    def copy(self):
        return self.replace()

    def replace(self, *args, **kwargs) -> RequestType:
        """Create a new Request with the same attributes except for those given new values"""
        for x in self.__slots__:
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

