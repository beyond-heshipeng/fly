import asyncio
import signal

from fly.spider import Spider, Request
from fly.download_middlewares.user_agent import UserAgentMiddleware
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
        "DOWNLOAD_TIMEOUT": 3,
        "DOWNLOAD_MIDDLEWARE": {
            "fly.download_middlewares.user_agent.UserAgentMiddleware": None,
        }
        # "SPIDER_MIDDLEWARE": [TestMiddleware]
    }

    start_urls = ["http://www.baidu.com", "http://www.baidu.com"]


if __name__ == '__main__':
    t = TestSpider()
    # asyncio.run(t.enqueue_request(Request(url="https://github.com/ttloveyy/sprite")))
    asyncio.run(t.enqueue_request(Request(url="https://github.com/ttloveyy/sprite")))
    asyncio.run(t.enqueue_request(Request(url="http://www.baidu.com")))
    asyncio.run(t.enqueue_request(Request(url="https://github.com/ttloveyy/sprite")))
    t.fly()
    # asyncio.run(t.enqueue_request(Request(url="https://github.com/ttloveyy/sprite")))