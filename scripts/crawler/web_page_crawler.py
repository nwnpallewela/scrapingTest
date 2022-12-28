from abc import ABC

from scrapy.crawler import CrawlerProcess

import json

from scripts.crawler.CrawlerProperties import CrawlerProperties
from scripts.crawler.MySpider import MySpider

if __name__ == '__main__':
    # Data Extraction
    f = open('../../configs.json')
    config = json.load(f)
    if True:
        print("Extracting web page data")
        process = CrawlerProcess()
        melbourne_crawler = MySpider()
        process.crawl(MySpider)
        process.start()

