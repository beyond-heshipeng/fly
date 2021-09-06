"""
This module contains the default values for all settings used by fly.
"""
from importlib import import_module

CONCURRENT_REQUESTS = 16

COOKIES_ENABLED = True

DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en',
}

DOWNLOAD_DELAY = 0
RANDOMIZE_DOWNLOAD_DELAY = False
# 1min
DOWNLOAD_TIMEOUT = 60
DOWNLOADER = 'fly.downloader.Downloader'
DOWNLOADER_MIDDLEWARES = {}

# log
LOG_ENABLED = True
LOG_ENCODING = 'utf-8'
LOG_FORMAT = '%(asctime)s [%(name)s] %(levelname)s: %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
LOG_STDOUT = False
LOG_LEVEL = 'DEBUG'
LOG_FILE = 'test.log'
LOG_SHORT_NAMES = False

# retry
RETRY_ENABLED = True
RETRY_TIMES = 2  # initial response + 2 retries = 3 requests
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 429]
RETRY_PRIORITY_ADJUST = -1

# don't obey robots.txt
ROBOTS_TXT_OBEY = False

SPIDER_MIDDLEWARES = []

USER_AGENT = f'Fly/{import_module("fly").__version__}'
