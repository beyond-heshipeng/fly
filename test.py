import asyncio
import signal

from fly.spider import Spider, Request
# from fly.spidermw import MiddlewareManager


# class TestMiddleware(SpiderMiddleware):
    # name = "test_middleware"

    # def __str__(self):
    #     return self.name
    #
    # def __repr__(self):
    #     return self.name
    # pass


class TestSpider(Spider):
    name = "Test Spider"
    custom_settings = {
        # "SPIDER_MIDDLEWARE": [TestMiddleware]
    }

    def parse(self, response):
        print(111)
        print(response.text)

    start_urls = ["http://www.baidu.com"]


if __name__ == '__main__':
    t = TestSpider()
    t.fly()
