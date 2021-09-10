import re
from urllib.parse import urljoin

from fly.http.response import Response
from fly.spiders import Spider, Request


class TestSpider(Spider):
    name = "Test Spider"
    custom_settings = {
        "DOWNLOAD_TIMEOUT": 20,
    }

    async def start_requests(self):
        start_requests = ["https://wenku.baidu.com/"]
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            # 'User-Agent': "Mozilla/5.0 (Windows NT 6.1; Win64; x64) "
            #               "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36",
            # 'X-Requested-With': 'XMLHttpRequest',
        }
        # for url in start_requests:
        return Request(url=start_requests[0], headers=headers, callback=self.callback_test)

    # start_urls = ["http://www.baidu.com", "http://www.baidu.com"]

    async def callback_test(self, response: Response):
        # print(response.body)
        print(re.findall(r"/blog/page/\d+/", response.body.decode()))
        for path in re.findall(r"/blog/page/\d+/", response.body.decode()):
            url = urljoin(response.url, path)
            print(url)
            yield Request(url=url)
        # print(re.findall(r"/blog/page/\d+/", response.body.decode()))


if __name__ == '__main__':
    t = TestSpider()
    # asyncio.run(t.enqueue_request(Request(url="https://github.com/ttloveyy/sprite")))
    # asyncio.run(t.enqueue_request(Request(url="https://github.com/ttloveyy/sprite")))
    # asyncio.run(t.enqueue_request(Request(url="https://www.zyte.com/blog/", callback=t.callback_test)))
    # asyncio.run(t.enqueue_request(Request(url="https://github.com/ttloveyy/sprite")))
    t.fly()
    # asyncio.run(t.enqueue_request(Request(url="https://github.com/ttloveyy/sprite")))
