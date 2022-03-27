import scrapy
import pandas as pd
from scrapy import Selector
from collections import defaultdict
import re
import csv

MY_URL_BASE = "en.wikipedia.org/wiki/"
DEFAULT_PROPS = ['born',
                 'education',
                 'alma_mater',
                 'spouse',
                 'parents',
                 'occupation',
                 'relatives']
EDUCATION_TYPE = ["education", "college", "alma mater"]
# NBSP = "&nbsp;"
NBSP = "\xa0"

"""Regular Expressions"""
VCARD_TABLE_CLASS = re.compile(r'infobox.*vcard')
DEGREE_RGX = re.compile(r'"\s(".*>.*</a>.*).*</')

def make_urls_list(my_url_base):
    urls_list = []
    with open('people.csv', 'r') as file:
        csvFile = csv.reader(file)
        for line in csvFile:
            print(line)
            my_url = my_url_base + line[0]
            print(f"my_url:{my_url}")
            urls_list.append(my_url)
    return urls_list


class PeopleSpider(scrapy.Spider):
    name = 'people'
    allowed_domains = ['en.wikipedia.org']
    global all_spouses_dict
    all_spouses_dict = defaultdict()
    global all_parents_dict
    all_parents_dict = defaultdict()
    url_base = 'http://en.wikipedia.org/wiki/'
    start_urls = make_urls_list(url_base)

    def parse(self, response):
        spouses_dict = defaultdict()
        parents_dict = defaultdict()
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
        # print(table_cls_str)
        my_infobox_trs = response.xpath(table_cls_str)

        people_dict = defaultdict()
        people_dict['schools'] = []
        people_dict['degrees'] = []
        people_dict['name'] = my_infobox_trs[0].xpath('th/div[@class="fn"]/text()').get()

        print(f"\n========  {people_dict['name']} ========")
        for tr in my_infobox_trs:
            if tr.xpath('th'):
                if tr.xpath('th/descendant-or-self::*/text()').get() not in [None, '']:
                    label_raw = tr.xpath('th/descendant-or-self::*/text()').get().lower()
                    label = label_raw.replace(NBSP, " ")
                    # print(label)
                    if label in EDUCATION_TYPE:
                        print(f"## {label} ##")
                        schools, degrees = self.get_education_data(tr)
                        people_dict['schools'] += schools
                        people_dict['degrees'] += degrees
                        print(people_dict['schools'])
                        print(people_dict['degrees'])
                        # continue
                    if label == 'spouse(s)':
                        print(f"## {label} ##")
                        people_dict, spouse_dict = self.get_spouse_data(tr, people_dict, spouses_dict)
                        all_spouses_dict.update(spouse_dict)
                    if label == 'parent(s)':
                        print(f"## {label} ##")
                        people_dict, parent_dict = self.get_parents_data(tr, people_dict, parents_dict)
                        all_parents_dict.update(parent_dict)
                    # if tr.xpath('th/a/text()').get():
                    #     label2 = tr.xpath('th/a/text()').get()
                    #     label += label2
                # if tr.xpath('td'):
                #     # print(tr.xpath('td/text()').get())
                #     if tr.xpath('td/a/text()'):
                #         val = tr.xpath('td/a/text()').get()
                #         # print(tr.getAttribute('href'))
                #     else:
                #         val = tr.xpath('td/text()').get()
                #     people_dict[label] = val
        print(people_dict)
        for k, v in all_spouses_dict.items():
            print(f"{k} -- {v}")

        for k, v in all_parents_dict.items():
            print(f"{k} -- {v}")

    def get_education_data(self, tr):
        # if tr.xpath('td//text()').get() not in [None, '']:
        #     print(tr.xpath('td//text()').get())
        if tr.xpath("td//child::a[position() mod 2 = 1]") not in [None, '']:
            my_odd_tags = tr.xpath('td//child::a[position() mod 2 = 1]')
            my_odd_list = [x.xpath('text()').get() for x in my_odd_tags]
            my_even_tags = tr.xpath('td//child::a[position() mod 2 = 0]')
            my_even_list = [x.xpath('text()').get() for x in my_even_tags]
            schools_list = []
            degrees_list = []
            for list_item in [my_odd_list, my_even_list]:
                for item in list_item:
                    if len(item) > 3:
                        schools_list.append(item)
                    else:
                        degrees_list.append(item)
        elif tr.xpath("tr//li/a"):
            ed_list = tr.xpath("tr//li/a/text()").get()
            for item in ed_list:
                print(item)
                if len(item) > 3:
                    schools_list.append(item)
                else:
                    degrees_list.append(item)

        return schools_list, degrees_list

    def get_spouse_data(self, my_spouse_data, my_people_dict, my_spouses_dict):
        spouse_list = []
        # my_spouses_dict = defaultdict()
        # if my_spouse_data.xpath('td/descendant-or-self::*/@href').get() not in [None, '']:
        if my_spouse_data.xpath('td//@href').get() not in [None, '']:
            spouse_href = my_spouse_data.xpath('td//@href')
            print(len(spouse_href))
            for wiki in spouse_href:
                spouse_name = wiki.get().split('/')[-1].replace('_', ' ')
                if not spouse_name.startswith('#'):
                    spouse_list.append(spouse_name)
                    my_spouses_dict[spouse_name] = wiki.get()
                    print(spouse_name)
                    print(f"wiki: {wiki.get()}")
            my_people_dict['spouses'] = spouse_list
        # elif my_spouse_data.xpath('td/descendant-or-self::*/div/text()').get() not in [None, '']:
        elif my_spouse_data.xpath('td//text()').get() not in [None, '']:
            spouse_name = my_spouse_data.xpath('td//text()').get()
            my_people_dict['spouses'] = spouse_name
            print(spouse_name)
        else:
            my_people_dict['spouse'] += 'unknown'
            print(f"Spouse cannot be retrieved from {my_spouse_data}")

        return my_people_dict, my_spouses_dict

    def get_parents_data(self, my_parent_data, my_people_dict, my_parents_dict):
        parents_list = []
        # my_parents_dict = defaultdict()
        if my_parent_data.xpath('td//@href').get() not in [None, '']:
            parent_href = my_parent_data.xpath('td//@href')
            print(len(parent_href))
            for wiki in parent_href:
                parent_name = wiki.get().split('/')[-1].replace('_', ' ')
                if not parent_name.startswith('#'):
                    parents_list.append(parent_name)
                    my_parents_dict[parent_name] = wiki.get()
                    print(parent_name)
                    print(f"wiki: {wiki.get()}")
            my_people_dict['parents'] = parents_list
        # elif my_spouse_data.xpath('td/descendant-or-self::*/div/text()').get() not in [None, '']:
        elif my_parent_data.xpath('td//text()').get() not in [None, '']:
            parent_name = get_parents_data.xpath('td//text()').get()
            my_people_dict['parents'] = parent_name
            print(parent_name)
        else:
            my_people_dict['spouse'] += 'unknown'
            print(f"Spouse cannot be retrieved from {my_parent_data}")

        return my_people_dict, my_parents_dict
