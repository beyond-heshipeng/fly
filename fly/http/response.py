"""
This module implements the Response class which is used to represent HTTP responses in fly.

"""

from urllib.parse import urljoin

from fly.http.headers import Headers
from fly.http.request import Request


class Response(object):
    """An object that represents an HTTP response, which is usually
    downloaded (by the Downloader) and fed to the Spiders for processing.
    """

    __slots__ = (
        "_headers",
        "_status",
        "_url",
        "_body",
        "_ip_address",
        "request"
    )

    def __init__(
        self,
        url: str,
        status: int = 200,
        headers: dict = None,
        body=b"",
        request: Request = None,
        ip_address: str = None,
    ):
        self._headers = Headers(headers or {})
        self._status = status

        self._url = url
        self._set_url(url)

        self._body = b""
        self._set_body(body)

        self.request = request
        self._ip_address = ip_address

    @property
    def meta(self):
        return self.request.meta

    @property
    def url(self):
        return self._url

    def _set_url(self, url):
        if isinstance(url, str):
            self._url = url
        else:
            raise TypeError(f'{type(self).__name__} url must be str, '
                            f'got {type(url).__name__}')

    @property
    def body(self):
        return self._body

    def _set_body(self, body):
        if body is None:
            self._body = b''
        elif not isinstance(body, bytes):
            raise TypeError(
                "Response body must be bytes. "
                "If you want to pass unicode body use TextResponse "
                "or HtmlResponse.")
        else:
            self._body = body

    @property
    def status(self):
        return self._status

    @property
    def headers(self):
        return self._headers

    def __str__(self):
        return f"<{self.status} {self.url}>"

    __repr__ = __str__

    def copy(self):
        """Return a copy of this Response"""
        return self.replace()

    def replace(self, *args, **kwargs):
        """Create a new Response with the same attributes except for those given new values"""
        for x in self.__slots__:
            kwargs.setdefault(x, getattr(self, x))
        cls = kwargs.pop('cls', self.__class__)
        return cls(*args, **kwargs)

    def urljoin(self, url):
        """Join this Response's url with a possible relative url to form an
        absolute interpretation of the latter."""
        return urljoin(self.url, url)
