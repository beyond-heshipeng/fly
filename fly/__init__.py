import pkgutil
import sys

# from fly.http.headers import Headers
# from fly.http.request import Request
# from fly.http.response import Response
# from fly.spider import Spider

__all__ = [
    '__version__', 'version_info',
    # 'Headers', 'Request', 'Response',
    # 'Spider'
]

__version__ = (pkgutil.get_data(__package__, "VERSION") or b"").decode("ascii").strip()
version_info = tuple(int(v) if v.isdigit() else v for v in __version__.split('.'))

# Check minimum required Python version
if sys.version_info < (3, 8):
    print("Scrapy %s requires Python 3.8+" % __version__)
    sys.exit(1)

del pkgutil
del sys
# del Headers
# del Request
# del Response
# del Spider
