import scrapy
from scrapy import Selector
from collections import defaultdict
import re

MY_URL_BASE = "en.wikipedia.org/wiki/"
DEFAULT_PROPS = ['born',
                 'education',
                 'alma_mater',
                 'spouse',
                 'parents',
                 'occupation',
                 'relatives']
EDUCATION_TYPE = ["education", "college", "alma mater"]
NBSP = "&nbsp;"

"""Regular Expressions"""
VCARD_TABLE_CLASS = re.compile(r'infobox.*vcard')


class PeopleSpider(scrapy.Spider):
    name = 'people'
    allowed_domains = ['en.wikipedia.org/wiki/']
    start_urls = ['http://en.wikipedia.org/wiki/Robert_Reich']
    # start_urls = ['http://en.wikipedia.org/wiki/Yuval_Noah_Harari']

    def parse(self, response):
        # print(response.xpath('//table[contains(@class,"vcard"]'))
        table_classes = response.css('.vcard').xpath("@class").extract()
        for cls in table_classes:
            match = re.search(VCARD_TABLE_CLASS, cls)
            if match:
                print("Class = {}".format(match.group(0)))
                table_cls = match.group(0)
            else:
                print("No Table Classes match vcard.")

        table_cls_str = "//table[@class='{}']/tbody/tr".format(table_cls)
        print(table_cls_str)
        my_infobox_trs = response.xpath(table_cls_str)

        people_dict = defaultdict()
        people_dict['name'] = my_infobox_trs[0].xpath('th/div/text()').get()

        for tr in my_infobox_trs:
            if tr.xpath('th'):
                if tr.xpath('th/text()').get() not in [None, '']:
                    label = tr.xpath('th/text()').get().lower()
                    # label = label_raw.replace(NBSP, " ")
                    print(label)
                    if label in EDUCATION_TYPE:
                        print("####### EDUCATION LIST #######")
                        education_list = tr.xpath('td')
                        self.get_education(education_list)
                    if tr.xpath('th/a/text()').get():
                        label2 = tr.xpath('th/a/text()').get()
                        label += label2
                    # print(title)
                    # people_dict[title] = None
                if tr.xpath('td'):
                    # print(tr.xpath('td/text()').get())
                    if tr.xpath('td/a/text()'):
                        val = tr.xpath('td/a/text()').get()
                        # print(tr.getAttribute('href'))
                    else:
                        val = tr.xpath('td/text()').get()
                    people_dict[label] = val
        print(people_dict)

    def get_education(self, edu_list):
        # print(edu_list)
        for ed in edu_list:
            if ed.xpath('a'):
                print(len(ed.xpath('a')))
                # for school in ed.xpath('a'):
                #     print(school.xpath('text()').get())
            if ed.xpath('span'):
                print(ed.xpath('span/a/text()').get())
