import pkgutil
import sys

__all__ = [
    '__version__', 'version_info',
]

__version__ = (pkgutil.get_data(__package__, "VERSION") or b"").decode("ascii").strip()
version_info = tuple(int(v) if v.isdigit() else v for v in __version__.split('.'))

# Check minimum required Python version
if sys.version_info < (3, 6):
    print("Scrapy %s requires Python 3.6+" % __version__)
    sys.exit(1)


del pkgutil
del sys
