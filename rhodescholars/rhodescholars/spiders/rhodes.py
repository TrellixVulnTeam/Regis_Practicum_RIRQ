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
        wikis = response.xpath('//td//span[@class="vcard"]/span/a/@href').getall()

        print(f"#### There are {len(wikis)} tds. ####")
        for wiki in wikis:
            wiki_page = wiki.split('/')[-1]
            # yield {
            #     'wiki_page': wiki_page
            # }

        trs = response.xpath('//table[@class="wikitable sortable"]/tbody//tr')
        for tr in trs:
            tds = tr.xpath('td')

            # Define the fields
            wiki_page = tds[0:1].xpath('span/span/span/a/@href').get()
            schools = tds[1:2].xpath('a/@href').getall()
            constituent_college = tds[2:3].xpath('a/@href').get()
            country = tds[4:5].xpath('text()').get()
            rhodes_scholar_year = tds[3:4].xpath('text()').get()
            notability = tds[5:6].xpath('text()').get()

            print(wiki_page)
            for school in schools:
                print(school)
            print(constituent_college)
            print(rhodes_scholar_year)
            print(country)
            print(notability)
            print()
