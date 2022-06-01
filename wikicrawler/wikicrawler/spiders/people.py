import scrapy
import pandas as pd
from scrapy import Selector
from collections import defaultdict
import re
import csv
from datetime import datetime as dt

MY_URL_BASE = "en.wikipedia.org/wiki/"
EDUCATION_TYPE = ["education", "college", "alma mater"]
DEFAULT_PROPS = ['born',
                 'education',
                 'college',
                 'alma_mater',
                 'spouse',
                 'parents',
                 'occupation',
                 'relatives']
RELATIVES_LABEL = ['parents',
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
# NBSP = "&nbsp;"
NBSP = "\xa0"

"""Regular Expressions"""
VCARD_TABLE_CLASS = re.compile(r'.*vcard')
DEGREE_RGX = re.compile(r'"\s(".*>.*</a>.*).*</')


def make_urls_list(my_url_base):
    urls_list = []

    with open('all_people.csv', 'r') as file:
        csvFile = csv.reader(file)
        for line in csvFile:
            urls_list.append(my_url_base + line[0])

    print(f"############### Length of URLs: {len(urls_list)} ###############")

    return urls_list


class PeopleSpider(scrapy.Spider):
    name = 'people'
    allowed_domains = ['en.wikipedia.org']

    global all_spouses_dict
    all_spouses_dict = defaultdict()

    global all_parents_dict
    all_parents_dict = defaultdict()

    global all_offspring_dict
    all_offspring_dict = defaultdict()

    global all_relatives_dict
    all_relatives_dict = defaultdict()

    url_base = 'http://en.wikipedia.org/wiki/'
    start_urls = make_urls_list(url_base)

    def parse(self, response):
        all_people_filename = 'all_people.csv'
        spouses_dict = defaultdict()
        parents_dict = defaultdict()
        offspring_dict = defaultdict()
        relatives_dict = defaultdict()
        # print(response.xpath('//table[contains(@class,"vcard"]'))
        table_classes = response.css('.vcard').xpath("@class").extract()
        for cls in table_classes:
            match = re.search(VCARD_TABLE_CLASS, cls)
            if match:
                # print("Class = {}".format(match.group(0)))
                table_cls = match.group(0)
            # else:
            #     print(f"No Table Classes match vcard {cls}")
        if not table_cls:
            print(f"No Table Classes match vcard {cls}")

        table_cls_str = "//table[@class='{}']/tbody/tr".format(table_cls)
        my_infobox_trs = response.xpath(table_cls_str)

        people_dict = defaultdict()
        # people_dict['schools'] = []
        # people_dict['degrees'] = []
        people_dict['name'] = my_infobox_trs[0].xpath('th/div[@class="fn"]/text()').get()

        print(f"\n========  {people_dict['name']} ========")
        # print(response.xpath("//tr//th/a[@title='Alma mater' or @title='Education']/../following-sibling::td[@class='infobox-data']//text()[starts-with(., ' (') or starts-with(., ',')]/following-sibling::a[1]/text()")).getall()
        # print(response.xpath("//tr//*[starts-with(text(), 'Education') or starts-with(text(), 'Alma mater')]/following-sibling::td[@class='infobox-data']//text()[starts-with(., ' (') or starts-with(., ',')]/preceding-sibling::a[1]/text()").getall())
        # print(response.xpath("//tr//*[starts-with(text(), 'Education') or starts-with(text(), 'Alma mater')]/following-sibling::td[@class='infobox-data']//text()[starts-with(., ' (') or starts-with(., ',')]/following-sibling::a[1]/text()").getall())

        for tr in my_infobox_trs:
            if tr.xpath('th'):
                # th = tr.xpath('th')
                if tr.xpath('th/descendant-or-self::*/text()').get() not in [None, '']:

                # if tr.xpath('th/descendant-or-self::*/text()').get() not in [None, '']:
                    label_raw = tr.xpath('th/descendant-or-self::*/text()').get().lower()
                    label = label_raw.replace(NBSP, " ")
                    # if label in EDUCATION_TYPE:
                    #     print(f"## {label} ##")
                    #     people_dict = self.get_education_data(tr, people_dict)
                    # if label == 'field':
                    #     print(f"## {label} ##")
                    # if label == 'doctoral advisor':
                    #     print(f"## {label} ##")
                    # if label == 'spouse(s)':
                    #     print(f"## {label} ##")
                    #     people_dict, spouse_dict = self.get_spouse_data(tr, people_dict, spouses_dict)
                    #     all_spouses_dict.update(spouse_dict)
                    # if label in ['parent', 'parent(s)']:
                    #     print(f"## {label} ##")
                    #     people_dict, parent_dict = self.get_parents_data(tr, people_dict, parents_dict)
                    #     all_parents_dict.update(parent_dict)
                    # if label == 'children':
                    #     print(f"## {label} ##")
                    #     people_dict, offspr_dict = self.get_offspring_data(tr, people_dict, offspring_dict)
                    #     all_offspring_dict.update(offspr_dict)
                    if label in ['born', 'date of birth']:
                        print(f'## {label} ##')
                        people_dict = self.get_bday(tr, people_dict)
                        # people_dict['full_name'] = tr.xpath("//div[@class='nickname']/text()").get()
                        # dob = dt.strptime(tr.xpath('//span[@class="bday"]/text()').get(), '%Y-%m-%d')
                        # people_dict['DOB'] = dob
                    if label == 'died':
                        print(f'## {label} ##')
                        people_dict = self.get_dday(tr, people_dict)

                # if label in ['relatives', 'members', 'relations']:
                    #     print(f'## {label} ##')
                    #     people_dict = self.get_relatives_data(tr, people_dict)
                    # if label == 'occupation':
                    #     print(f'## {label} ##')
                    #     people_dict = self.get_occupation_data(tr, people_dict)
                    # if label == 'citizenship':
                    #     print(f'## {label} ##')
                    #     # TODO: Grab citizenship data
                    # if label == 'political party':
                    #     print(f'## {label} ##')
                    #     # TODO: Grab political party dta
                    # if label == 'organization':
                    #     print(f'## {label} ##')
                    # if label == 'known for':
                    #     print(f'## {label} ##')
                    # if label == 'title':
                    #     print(f'## {label} ##')
                    # if label == 'board member of':
                    #     print(f'## {label} ##')
                    # if label == 'labels':
                    #     print(f'## {label} ##')

        # print(people_dict)
        yield people_dict
        # print("____Yielded people_dict____")

        # spouse_names = list(all_spouses_dict.values())
        # parents_names = list(all_parents_dict.values())
        # offspring_names = list(all_offspring_dict.values())
        #
        # with open(all_people_filename, 'w', newline='') as f:
        #     csv_writer = csv.writer(f, lineterminator='\n')
        #     for val in spouse_names:
        #         csv_writer.writerow([val])
        #     for val in parents_names:
        #         csv_writer.writerow([val])
        #     for val in offspring_names:
        #         csv_writer.writerow([val])

    def get_music_labels(self, tr):
        pass

    def get_board_member_data(self, tr):
        pass

    def get_political_party(self, tr):
        pass

    def organization(self, tr):
        pass

    def get_citizenship(self, tr):
        pass

    def get_known_for(self, tr):
        pass

    def get_title(self, tr):
        pass

    def get_dday(self, tr, my_people_dict):
        if tr.xpath('td/text()').get():
            my_people_dict['died'] = tr.xpath('td/text()').get()

            return my_people_dict

    def get_bday(self, tr, my_people_dict):
        if tr.xpath("//div[@class='nickname']/text()").get():
            my_people_dict['full_name'] = tr.xpath("//div[@class='nickname']/text()").get()

        if tr.xpath('//span[@class="bday"]/text()').get():
            my_people_dict['born'] = dt.strptime(tr.xpath('//span[@class="bday"]/text()').get(), '%Y-%m-%d')
        elif tr.xpath('td/text()').get():
            my_people_dict['born'] = tr.xpath('td/text()').get()

        return my_people_dict

    def get_occupation_data(self, tr, my_people_dict):
        if tr.xpath('td//a/text()'):
            occupations = tr.xpath('td//a/text()').getall()
            my_people_dict['occupation'] = occupations
        elif tr.xpath('td/text()').get():
            my_people_dict['occupation'] = tr.xpath('td/text()').get()
        print(my_people_dict['occupation'])

        return my_people_dict

    def get_relatives_data(self, tr, my_people_dict):
        if tr.xpath('td//@href') not in [None, '']:
            td = tr.xpath('td/text()').get()
            relatives = tr.xpath('td//@href').getall()
            for relative in relatives:
                my_people_dict['relatives'] += relative

        return my_people_dict

    def get_offspring_data(self, my_offspring_data, my_people_dict, my_offspring_dict):
        offspring_list = []
        if my_offspring_data.xpath('td//@href').get() not in [None, '']:
            offspring_href = my_offspring_data.xpath('td//@href')
            print(f"Found offspring hrefs!")
            for wiki in offspring_href:
                offspring_name = wiki.get().split('/')[-1].replace('_', ' ')
                if not offspring_name.startswith('#'):
                    offspring_list.append(offspring_name)
                    wiki_page_name =  wiki.get().split('/')[-1]
                    my_offspring_dict[offspring_name] = wiki_page_name
                    # print(f"Offspring name: {offspring_name}")
                    # print(f"wiki: {wiki_page_name}")
            my_people_dict['offspring'] = offspring_list
            # elif my_spouse_data.xpath('td/descendant-or-self::*/div/text()').get() not in [None, '']:
        elif my_offspring_data.xpath('td//text()').get() not in [None, '']:
            offspring_name = my_offspring_data.xpath('td//text()').get()
            my_people_dict['offspring'] = offspring_name
            # print(f"Number of offspring: {offspring_name}")
        else:
            my_people_dict['offspring'] += 'unknown'
            print(f"Offspring cannot be retrieved from {my_offspring_data}")
        return  my_people_dict, my_offspring_dict

    def get_spouse_data(self, my_spouse_data, my_people_dict, my_spouses_dict):
        spouse_list = []
        # if my_spouse_data.xpath('td/descendant-or-self::*/@href').get() not in [None, '']:
        if my_spouse_data.xpath('td//@href').get() not in [None, '']:
            spouse_href = my_spouse_data.xpath('td//@href').get()
            print(len(spouse_href))
            for wiki in spouse_href:
                spouse_name = wiki.get().split('/')[-1].replace('_', ' ')
                if not spouse_name.startswith('#'):
                    spouse_list.append(spouse_name)
                    wiki_page_name = wiki.get().split('/')[-1]
                    my_spouses_dict[spouse_name] = wiki_page_name
                    # print(spouse_name)
                    # print(f"wiki: {wiki_page_name}")
            my_people_dict['spouses'] = spouse_list
        # elif my_spouse_data.xpath('td/descendant-or-self::*/div/text()').get() not in [None, '']:
        elif my_spouse_data.xpath('td//text()').get() not in [None, '']:
            spouse_name = my_spouse_data.xpath('td//text()').get()
            my_people_dict['spouses'] = spouse_name
            # print(spouse_name)
        else:
            my_people_dict['spouse'] += 'unknown'
            print(f"Spouse cannot be retrieved from {my_spouse_data}")

        return my_people_dict, my_spouses_dict

    def get_parents_data(self, my_parent_data, my_people_dict, my_parents_dict):
        parents_list = []
        if my_parent_data.xpath('td//@href').get() not in [None, '']:
            parent_href = my_parent_data.xpath('td//@href')
            print(len(parent_href))
            for wiki in parent_href:
                parent_name = wiki.get().split('/')[-1].replace('_', ' ')
                if not parent_name.startswith('#'):
                    parents_list.append(parent_name)
                    wiki_page_name = wiki.get().split('/')[-1]
                    my_parents_dict[parent_name] = wiki_page_name
                    # print(parent_name)
                    # print(f"wiki: {wiki_page_name}")
            my_people_dict['parents'] = parents_list
        # elif my_spouse_data.xpath('td/descendant-or-self::*/div/text()').get() not in [None, '']:
        elif my_parent_data.xpath('td//text()').get() not in [None, '']:
            parent_name = my_parent_data.xpath('td//text()').get()
            my_people_dict['parents'] = parent_name
            # print(parent_name)
        else:
            my_people_dict['parents'] += 'unknown'
            print(f"Parents cannot be retrieved from {my_parent_data}")

        return my_people_dict, my_parents_dict

    def get_education_data(self, tr, my_people_dict):
        schools_list = []
        degrees_list = []
        degrees_list_no_anchor = tr.xpath(
            "//*[starts-with(text(), 'Education') or starts-with(text(), 'Alma mater')]/following-sibling::td[@class='infobox-data']//text()[starts-with(., ' (') or starts-with(., ',')]/following-sibling::a[1]/text()").getall()
        school_list_no_anchor = tr.xpath(
            "//*[starts-with(text(), 'Education') or starts-with(text(), 'Alma mater')]/following-sibling::td[@class='infobox-data']//text()[starts-with(., ' (')]/preceding-sibling::a[1]/text()").getall()

        degrees_list_anchor = tr.xpath(
            "//a[starts-with(text(), 'Education') or starts-with(text(), 'Alma mater')]/../following-sibling::td[@class='infobox-data']//text()[starts-with(., ' (') or starts-with(., ',')]/following-sibling::a[1]/text()").getall()
        school_list_anchor = tr.xpath(
            "//a[starts-with(text(), 'Education') or starts-with(text(), 'Alma mater')]/../following-sibling::td[@class='infobox-data']//text()[starts-with(., ' (')]/preceding-sibling::a[1]/text()").getall()

        degrees_list_small = tr.xpath(
            "//*[starts-with(text(), 'Education') or starts-with(text(), 'Alma mater')]/following-sibling::td[@class='infobox-data']//text()[starts-with(., '(') or starts-with(., ',')]/following-sibling::a[1]/text()").getall()
        school_list_small = tr.xpath(
            "//*[starts-with(text(), 'Education') or starts-with(text(), 'Alma mater')]/following-sibling::td[@class='infobox-data']//text()[starts-with(., '(')]/../preceding-sibling::a[1]/text()").getall()

        # TODO: These lines could be another method. Send two lists of the above lists and append to degrees/schools
        # TODO cont... lists, then cleanup before returning to this method
        if degrees_list_no_anchor:
            degrees_list += degrees_list_no_anchor
        if degrees_list_anchor:
            degrees_list += degrees_list_anchor
        if degrees_list_small:
            degrees_list += degrees_list_small

        if school_list_no_anchor:
            schools_list += school_list_no_anchor
        if school_list_anchor:
            schools_list += school_list_anchor
        if school_list_small:
            schools_list += school_list_small

        for d in degrees_list:
            if d in schools_list:
                degrees_list.remove(d)

        if not schools_list:
            schools_list = tr.xpath('td//a/text()').getall()

        my_people_dict['schools'] += schools_list
        my_people_dict['degrees'] += list(set(degrees_list))

        return my_people_dict
