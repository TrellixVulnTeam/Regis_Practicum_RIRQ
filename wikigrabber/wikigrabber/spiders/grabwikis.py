import scrapy
import sys
import re
import os
import csv
import csv

from scrapy.crawler import CrawlerProcess
from functools import reduce

# Global Variable Declarations
MY_URL_BASE = "en.wikipedia.org/wiki/"

"""Regular Expressions"""
VCARD_TABLE_CLASS = re.compile(r'infobox.*')
PREFS_LIST = ["Wikipedia", "index.php", "#"]
NBSP = "\xa0"
HREFS_LABEL = ['parents',
               'parent(s)',
               'spouse(s)',
               'relatives',
               'members',
               'relations',
               'influences',
               'influenced',
               'children',
               'preceded by',
               'succeeded by',
               'connected',
               'teacher(s)',
               'mentor(s)',
               'deputy',
               'president',
               'vice president',
               'partner(s)',
               'domestic partner']
FAMILY_REGEX = re.compile(r'.*family')

# //div[@class='treeview']//li//@href
# //*[@id="mw-content-text"]/div[1]/div[5]/pre/text()[8]
# ∞ 1770 : Gertrude Schnapper (1753–1849)
# │ └──>
# //*[@id="mw-content-text"]/div[1]/div[5]/pre/text()[2]


def make_urls_list(my_url_base):
    urls_list = []

    # with open('people.csv', 'r') as file:
    #     csvFile = csv.reader(file)
    #     for line in csvFile:
    #         if line[0] not in names_list:
    #             names_list.append(line[0])

    with open('people_base.csv', 'r') as file:
        csv_reader = csv.reader(file)
        first_row = next(csv_reader)
        if first_row != 'wiki':
            urls_list.append(my_url_base + first_row[0])
        for line in csv_reader:
            urls_list.append(my_url_base + line[0])

    print(f"############### Length of URLs: {len(urls_list)} ###############")

    return urls_list


def csv_reader(csv_file):
    final_list = []

    with open(csv_file, 'r') as f:
        input_list = csv.reader(f)

        for row in input_list:
            final_list.append(row[0])

    return final_list


def add_new_wikis(adding_file, gaining_file, base_file):
    """
    Adds newly discovered wiki pages to an accumulative wiki pages file before deleting the previous base file
    used to extract the new wikis. The previous base file is then deleted and the adding_file is renamed to base_file
    for the next grabwikis spider run.
    """
    adding_list = csv_reader(adding_file)
    gaining_list = csv_reader(gaining_file)
    adding_set = set(adding_list)
    gaining_set = set(gaining_list)

    new_wikis = list(set.difference(adding_set, gaining_set))
    print(len(new_wikis))

    csv_dict_writer(gaining_file, new_wikis, 'a')
    csv_dict_writer(base_file, new_wikis, 'w')
    os.remove(adding_file)


def csv_dict_writer(my_file, my_list, my_mode):
    with open(my_file, my_mode, newline='') as f:

        writer = csv.DictWriter(f, fieldnames=['wiki'])

        for row in my_list:

            if row != 'wiki' or 'Wikipedia:' not in row:
                writer.writerow({'wiki': row})


def csv_writer(out_file, my_list):
    with open(out_file, 'w', newline='') as outfile:
        csv_writer = csv.writer(outfile)

        for row in my_list:
            csv_writer.writerows(row)


class GrabwikisSpider(scrapy.Spider):
    name = 'grabwikis'
    allowed_domains = ['en.wikipedia.org']
    url_base = 'http://en.wikipedia.org/wiki/'
    start_urls = make_urls_list(url_base)

    def parse(self, response):
        table_classes = response.css('.infobox').xpath("@class").extract()
        if not table_classes:
            print("#### NO Table Classes ####")
        for cls in table_classes:
            match = re.search(VCARD_TABLE_CLASS, cls)
            if match:
                print("Class = {}".format(match.group(0)))
                table_cls = match.group(0)
                break

        if not table_cls:
            print(f"No Table Classes match vcard {cls}")
            return

        table_cls_str = "//table[@class='{}']/tbody/tr".format(table_cls)
        my_infobox_trs = response.xpath(table_cls_str)
        person = my_infobox_trs[0].xpath('th/div[@class="fn"]/text()').get()
        print(f"\n======== Grabbing relatives wiki pages for {person} ========")

        for tr in my_infobox_trs:
            # if tr.xpath('th'):
            wikis = None
            if tr.xpath('th/descendant-or-self::*/text()').get() not in [None, '']:
                # if tr.xpath('th/descendant-or-self::*/text()').get() not in [None, '']:
                label_raw = tr.xpath('th/descendant-or-self::*/text()').get().lower()
                label = label_raw.replace(NBSP, " ")
                # if label == 'spouse(s)':
                #     print(f"## {label} ##")
                #     wikis = (self.get_spouse_data(tr))
                # if label in ['parent', 'parent(s)']:
                #     print(f"## {label} ##")
                #     wikis = self.get_parents_data(tr)
                # if label == 'children':
                #     print(f"## {label} ##")
                #     wikis = self.get_offspring_data(tr)
                if label in HREFS_LABEL:
                    print(f'## {label} ##')
                    wikis = self.get_hrefs_data(tr)

            if wikis:
                if isinstance(wikis, list):
                    for wiki in wikis:
                        if wiki.startswith('/wiki/'):
                            print(wiki)
                            yield {'wiki': wiki.split('/')[-1]}
                elif isinstance(wikis, str):
                    if wikis.startswith('/wiki/'):
                        print(wikis)
                        yield {'wiki': wikis.split('/')[-1]}

    def get_hrefs_data(self, tr):
        if tr.xpath('td//@href') not in [None, '']:
            hrefs = tr.xpath('td//@href').getall()
            # print(list(relatives))
            return hrefs
        else:
            return None
