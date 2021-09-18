import asyncio

from fly import Spider
from fly.engine import Engine
from fly.scheduler import Scheduler


class Crawler:
    def __init__(self, scheduler: Scheduler = None):
        self.spiders = set()
        self.engine = Engine(scheduler)

    def crawl(self, spider: Spider):
        self.spiders.add(spider)

    def start(self):
        loop = asyncio.get_event_loop()
        self.engine.start()
        # loop.run_until_complete()
