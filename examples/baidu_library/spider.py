from fly import Response, Spider, Request


class BaiduLibrarySpider(Spider):
    name = "baidu library spider"
    custom_settings = {
        "DOWNLOAD_TIMEOUT": 20,
        "DOWNLOADER": "downloader.PyppeteerDownloader",
        "HEADLESS": False,
        "USER_DATA_DIR": "./cache"
    }

    async def start_requests(self):
        start_requests = ["https://wenku.baidu.com/"]
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36",
        }
        for url in start_requests:
            return Request(url, headers=headers, callback=self.parse)

    async def parse(self, response: Response):
        print(response.body.decode())


if __name__ == '__main__':
    t = BaiduLibrarySpider()
    t.fly()
