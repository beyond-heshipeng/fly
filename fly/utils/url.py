from urllib.parse import urldefrag, urlparse, ParseResult
from w3lib.url import add_or_replace_parameter

from fly.utils.python import to_unicode


def escape_ajax(url):
    """
    Return the crawleable url according to:
    https://developers.google.com/webmasters/ajax-crawling/docs/getting-started

    >>> escape_ajax("www.example.com/ajax.html#!key=value")
    'www.example.com/ajax.html?_escaped_fragment_=key%3Dvalue'
    >>> escape_ajax("www.example.com/ajax.html?k1=v1&k2=v2#!key=value")
    'www.example.com/ajax.html?k1=v1&k2=v2&_escaped_fragment_=key%3Dvalue'
    >>> escape_ajax("www.example.com/ajax.html?#!key=value")
    'www.example.com/ajax.html?_escaped_fragment_=key%3Dvalue'
    >>> escape_ajax("www.example.com/ajax.html#!")
    'www.example.com/ajax.html?_escaped_fragment_='

    URLs that are not "AJAX crawlable" (according to Google) returned as-is:

    >>> escape_ajax("www.example.com/ajax.html#key=value")
    'www.example.com/ajax.html#key=value'
    >>> escape_ajax("www.example.com/ajax.html#")
    'www.example.com/ajax.html#'
    >>> escape_ajax("www.example.com/ajax.html")
    'www.example.com/ajax.html'
    """
    defrag, frag = urldefrag(url)
    if not frag.startswith('!'):
        return url
    return add_or_replace_parameter(defrag, '_escaped_fragment_', frag[1:])


def parse_url(url, encoding=None):
    """Return urlparsed url from the given argument (which could be an already
    parsed url)
    """
    if isinstance(url, ParseResult):
        return url
    return urlparse(to_unicode(url, encoding))


def url_is_from_any_domain(url, domains):
    """Return True if the url belongs to any of the given domains"""
    host = parse_url(url).netloc.lower()
    if not host:
        return False
    domains = [d.lower() for d in domains]
    return any((host == d) or (host.endswith(f'.{d}')) for d in domains)


def url_is_from_spider(url, spider):
    """Return True if the url belongs to the given spider"""
    return url_is_from_any_domain(url, [spider.name] + list(getattr(spider, 'allowed_domains', [])))
