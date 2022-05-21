import scrapy
from datetime import datetime as dt
from scrapy import Selector


class RhodesSpider(scrapy.Spider):
    name = 'rhodes'
    allowed_domains = ['en.wikipedia.org']
    start_urls = ['http://en.wikipedia.org/wiki/List_of_Rhodes_Scholars']

    def parse(self, response):
        wikis = response.xpath('//td//span[@class="vcard"]/span/a/@href').getall()

        print(f"#### There are {len(wikis)} tds. ####")
        for wiki in wikis:
            wiki_page = wiki.split('/')[-1]
            yield {
                'wiki_page': wiki_page
            }

        trs = response.xpath('//table[@class="wikitable sortable"]/tbody//tr')
        for tr in trs:
            tds = tr.xpath('td')

            # Define the fields
            wiki_page = tds[0:1].xpath('span/span/span/a/@href').get()
            if wiki_page is None:
                continue
            wiki_name = str(wiki_page).split('/')[-1].strip(')')
            name = wiki_name.replace('_', ' ')
            if ' (' in name:
                occupation = name.split(' (')[1]
                name = name.split(' (')[0].strip()
            else:
                occupation = None
            schools = tds[1:2].xpath('a/@href').getall()
            constituent_college = tds[2:3].xpath('a/@href').get()
            country = tds[4:5].xpath('text()').get()
            year_awarded = str(tds[3:4].xpath('text()').get()).strip()
            # rhodes_scholar_year = dt.strptime(year_awarded, '%Y')
            notability = tds[5:6].xpath('text()').get()

            print(name)
            print(year_awarded)
            # for school in schools:
            #     print(school)
            # print(constituent_college)
            # print(rhodes_scholar_year)
            # print(country)
            # print(notability)
            print(occupation)
            print()
            # yield {
            #     'name': name,
            #     'occupation': occupation,
            #     'rhodes_scholar_year': year_awarded,
            # }
