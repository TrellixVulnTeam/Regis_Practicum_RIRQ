import scrapy
import pandas as pd
from scrapy import Selector
from collections import defaultdict
import re
import csv
from datetime import datetime as dt


class RhodesSpider(scrapy.Spider):
    name = 'rhodes'
    allowed_domains = ['en.wikipedia.org']
    start_urls = ['http://en.wikipedia.org/wiki/List_of_Rhodes_Scholars']

    def parse(self, response):
        tds = response.xpath('//td//span[@class="vcard"]/span/a/@href').getall()

        print(f"#### There are {len(tds)} tds. ####")
        for wiki in tds:
            wiki_page = wiki.split('/')[-1]
            yield {
                'wiki_page': wiki_page
            }
