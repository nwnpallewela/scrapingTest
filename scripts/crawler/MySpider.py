import csv
from abc import ABC

from scrapy.spiders import CrawlSpider, Rule, Spider
from scrapy.linkextractors import LinkExtractor

from scripts.crawler.CrawlerProperties import CrawlerProperties


class MySpider(CrawlSpider, ABC):
    name = 'City Council of pesaro'
    folder = 'pesaro'
    allowed_domains = ['www.comune.pesaro.pu.it']
    # allowed_domains = ['www.act.gov.au', 'www.accesscanberra.act.gov.au','yoursayconversations.act.gov.au']
    start_urls = ['http://www.comune.pesaro.pu.it/']
    # start_urls = ['https://www.act.gov.au', 'https://www.accesscanberra.act.gov.au/s/',
    #               'https://www.act.gov.au/our-canberra/home']
    count = 0
    rules = (
        # Extract links matching 'category.php' (but not matching 'subsection.php')
        # and follow links from them (since no callback means follow=True by default).
        # Rule(LinkExtractor(allow=('category\.php',), deny=('/modulistica/index.php?action=',))),
        # Extract links matching 'item.php' and parse them with the spider's method parse_item
        Rule(LinkExtractor(deny=('/en-us/')),
             callback='parse_item', follow=True),
    )
    custom_settings = {
        "DEPTH_LIMIT": 3,
        "USER_AGENT": 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) '
                      'AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'
    }

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        # with open("files/aus/melbourne/site_urls.csv", mode='w') as site_url_file:
        with open("files/italy/" + self.folder + "/site_urls.csv", mode='w') as site_url_file:
            site_url_writer = csv.DictWriter(site_url_file, fieldnames=['council', 'page', 'url'])
            site_url_writer.writeheader()
            site_url_file.close()

    def parse_item(self, response):
        self.logger.info('Hi, this is an item page! %s', response.url)
        self.count = self.count + 1
        print(str(self.count) + ' - ' + response.url)
        self.write_row_to_csv({'council': 102, 'page': self.count, 'url': response.url})

    def write_row_to_csv(self, row):
        # with open('files/aus/melbourne/site_urls.csv', 'a', newline='\n') as site_url_file:
        with open('files/italy/' + self.folder + '/site_urls.csv', 'a', newline='\n') as site_url_file:
            site_url_writer = csv.DictWriter(site_url_file, fieldnames=['council', 'page', 'url'])
            site_url_writer.writerow(row)
            site_url_file.close()
