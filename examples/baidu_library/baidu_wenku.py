from lxml import html
from fly import Response, Spider, Request


class BaiduLibrarySpider(Spider):
    name = "baidu library spiders"
    custom_settings = {
        "DOWNLOAD_TIMEOUT": 60,
        "DOWNLOADER": "downloader.PyppeteerDownloader",
        "HEADLESS": False,
        "USER_DATA_DIR": "./cache"
    }

    async def start_requests(self):
        start_requests = [
            "https://wenku.baidu.com/search?word=智慧能源ppt"
            "&lm=0&od=0&fr=top_home&ie=utf-8&pn=1",
            "https://wenku.baidu.com/search?word=智慧能源ppt"
            "&lm=0&od=0&fr=top_home&ie=utf-8&pn=2",
            "https://wenku.baidu.com/search?word=智慧能源ppt"
            "&lm=0&od=0&fr=top_home&ie=utf-8&pn=3"
        ]
        for url in start_requests:
            return Request(url, callback=self.parse_list)

    async def parse_list(self, response: Response):
        tree = html.fromstring(response.body.decode())
        items = tree.xpath("//div[@class='search-result-wrap']")

        javascript = """
            () => {
                 let elements = document.getElementsByClassName("read-all");
                 if (elements && elements.length > 0) {
                    elements[0].click();
                    return document.body;
                 }
            }
        """

        for item in items:
            if item.xpath(".//div[@class='doc-icon doc-icon-ppt']"):
                url = item.xpath(".//a[@class='search-result-title']/@href")
                if url:
                    self.logger.info(f"extract link {url[0]} from {response.url}")
                    yield Request(url[0], callback=self.parse_detail, meta={"javascript": javascript})

    async def parse_detail(self, response: Response):
        tree = html.fromstring(response.body.decode())
        title = tree.xpath("//h3[@class='doc-title']//text()")
        image = (tree.xpath("//img[starts-with(@src, 'https://wkretype.bdimg.com/retype/zoom')]/@src")
                 .extend(tree.xpath("//img[starts-with(@data-src, "
                                    "'https://wkretype.bdimg.com/retype/zoom')]/@data-src")))
        summary = tree.xpath("//div[@class='doc-summary-wrap']//text()")
        print(title, image, summary)


if __name__ == '__main__':
    t = BaiduLibrarySpider()
    t.fly()
