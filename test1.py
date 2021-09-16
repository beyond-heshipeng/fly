import hashlib
import os
import re
import sys


import asyncio

import requests
from lxml import html
from pyppeteer import launch
from pyppeteer.errors import PageError

if sys.version_info >= (3, 8) and sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def fetch(url):
    browser = await launch(userDataDir="./examples/baidu_wenku/cache",
                           autoClose=False,
                           options={'args': ['--no-sandbox', '--disable-gpu']})
    page = await browser.newPage()
    await page.setUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/93.0.4577.63 Safari/537.36")
    try:

        options = {"timeout": 60000}
        await page.goto(url, options=options)
        await page.evaluate('''
                    () => {
                        let elements = document.getElementsByClassName("read-all");
                        if (elements && elements.length > 0) {
                           elements[0].click();
                           window.scrollTo(0, 5000);
                        }
                   }
               ''')

        response = await page.content()
        return response
    except PageError as err:
        print(err)
        return None, PageError
    finally:
        await page.close()
        await browser.close()


def md5(string):
    h1 = hashlib.md5()
    h1.update(string.encode(encoding="utf-8"))
    return h1.hexdigest()


if __name__ == '__main__':
    start_requests = [
        "https://wenku.baidu.com/search?word=智慧能源ppt"
        "&lm=0&od=0&fr=top_home&ie=utf-8&pn=1",
        "https://wenku.baidu.com/search?word=智慧能源ppt"
        "&lm=0&od=0&fr=top_home&ie=utf-8&pn=2",
        "https://wenku.baidu.com/search?word=智慧能源ppt"
        "&lm=0&od=0&fr=top_home&ie=utf-8&pn=3"
    ]

    url = "http://110.40.183.167:8000/ocr/ppt_ocr"

    async def parse_detail(response):
        tree = html.fromstring(response)
        title = tree.xpath("//h3[@class='doc-title']//text()")
        tags = tree.xpath("//div[@class='doc-tag-wrap']/div//text()")
        tags = [tag.strip().replace("\n", "") for tag in tags if tag != ""]
        summary = "".join(tree.xpath("//div[@class='doc-summary-wrap']//text()"))
        score = re.findall(r"([0-9.]+)分", summary)
        read_times = re.findall(r"([0-9]+)阅读", summary)
        download_times = re.findall(r"([0-9]+)下载", summary)
        upload_time = re.findall(r"([0-9]{4}-[0-9]{2}-[0-9]{2})上传", summary)
        pages = re.findall(r"([0-9]+)页", summary)
        size = re.findall(r"([0-9.]+)MB", summary)

        images = []
        images.extend(tree.xpath("//img[starts-with(@src, 'https://wkretype.bdimg.com/retype/zoom')]/@src"))
        images.extend(tree.xpath("//img[starts-with(@data-src, 'https://wkretype.bdimg.com/retype/zoom')]/@data-src"))

        print(title, tags, score, read_times, download_times, upload_time, pages, size, images)

        # for image in images:
        #     body = {
        #         "doc_title": title[0],
        #         "image": image,
        #         "image_time": time[0]
        #     }
        #     print(body)

        global ppt_count
        path = f"ppt/ppt_demo_{ppt_count}/"
        if not os.path.exists(path):
            os.mkdir(path)

        with open(f"{path}/summary.txt", "w+", encoding="utf-8") as f:
            f.write(f"title: {title[0]}\n")
            f.write(f"tags: {','.join(tags)}\n")
            f.write(f"score: {score[0]}\n")
            f.write(f"read_times: {read_times[0]}\n")
            f.write(f"download_times: {download_times[0]}\n")
            f.write(f"upload_times: {upload_time[0]}\n")
            f.write(f"pages: {pages[0]}\n")
            f.write(f"size: {size[0]}\n")

        for index, image in enumerate(images):
            with open(f"{path}/{index}.jpg", "wb") as f:
                f.write(requests.get(image).content)
        ppt_count += 1

            # resp = requests.post(url, json=body, headers={"Content-Type": "application/json"})
            # print(resp.status_code, resp.text)

    async def run():
        await fetch("https://wenku.baidu.com/view/cf49cbf2fc4ffe473268ab15.html?"
                    "fixfr=Ax%252BBl%252F3KXo7ygXE8umqIUA%253D%253D&fr=income1-wk_go_search-search")
        for url in start_requests:
            resp = await fetch(url)
            # print(resp)

            tree = html.fromstring(resp)
            items = tree.xpath("//div[@class='search-result-wrap']")

            for item in items:
                if item.xpath(".//div[@class='doc-icon doc-icon-ppt']"):
                    url = item.xpath(".//a[@class='search-result-title']/@href")
                    if url:
                        print(url[0])
                        await parse_detail(await fetch(url[0]))

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
