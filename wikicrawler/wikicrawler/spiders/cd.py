import scrapy


class CdSpider(scrapy.Spider):
    name = 'cd'
    allowed_domains = ['wikicrawler']
    start_urls = ['http://wikicrawler/']

    def parse(self, response):
        pass
