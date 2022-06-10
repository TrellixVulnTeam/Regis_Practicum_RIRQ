import scrapy
import urllib
import re
import csv
import neo4j
# import pandas as pd

from collections import defaultdict
# from scrapy import Selector
from datetime import datetime as dt

############## Neo4j References ##############
# https://neo4j.com/developer/desktop-csv-import/
# https://discourse.neo4j.com/t/how-to-format-lists-in-the-node-property-when-using-the-neo4j-admin-import-tool/35766

MY_URL_BASE = "en.wikipedia.org/wiki/"
EDUCATION_TYPE = ["education", "college", "alma mater"]
REMOVE_HEADERS = ['Personal details', 'Signature', 'Names']
DEFAULT_PROPS = ['born',
                 'education',
                 'college',
                 'alma_mater',
                 'spouse',
                 'parents',
                 'occupation',
                 'profession',
                 'relatives']
RELATIVES_LABEL = ['parents',
                   'parent(s)',
                   'mother',
                   'father',
                   'spouse(s)',
                   'relatives',
                   'family',
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

    with open('all_people.csv', 'r', encoding='unicode_escape') as file:
        csvFile = csv.reader(file)
        for line in csvFile:
            urls_list.append(my_url_base + line[0])

    print(f"############### Length of URLs: {len(urls_list)} ###############")

    return urls_list


class PeopleSpider(scrapy.Spider):
    name = 'people'
    allowed_domains = ['en.wikipedia.org']

    # global all_spouses_dict
    # all_spouses_dict = defaultdict()

    global all_parents_dict
    all_parents_dict = defaultdict()

    global all_offspring_dict
    all_offspring_dict = defaultdict()

    global all_relatives_dict
    all_relatives_dict = defaultdict()

    url_base = 'http://en.wikipedia.org/wiki/'
    # start_urls = make_urls_list(url_base)
    start_urls = ['http://en.wikipedia.org/wiki/Alec_Baldwin',
                  'http://en.wikipedia.org/wiki/Jared_Leto',
                  'http://en.wikipedia.org/wiki/Elon_Musk',
                  'http://en.wikipedia.org/wiki/Charles,_Prince_of_Wales',
                  'http://en.wikipedia.org/wiki/Kat_Timpf',
                  'http://en.wikipedia.org/wiki/Charles_Aznavour']

    def parse(self, response):
        all_people_filename = 'all_people.csv'
        spouses_dict = defaultdict()
        parents_dict = defaultdict()
        relatives_dict = defaultdict()
        offspring_dict = defaultdict()
        people_dict = defaultdict()

        # print(response.xpath('//table[contains(@class,"vcard"]'))
        table_classes = response.css('.vcard').xpath("@class").extract()
        try:
            for cls in table_classes:
                match = re.search(VCARD_TABLE_CLASS, cls)
                if match:
                    table_cls = match.group(0)
                    print(f"Class = {table_cls}")
                    table_cls_str = f"//table[@class='{table_cls}']/tbody//tr"
                    print(f"table_cls_str: {table_cls_str}")
                    my_infobox_trs = response.xpath(table_cls_str)
                    print(f"my_infobox_trs: {my_infobox_trs}")
                    raw_name = my_infobox_trs.xpath('.//*[contains(@class, "fn")]/text()').get()
                    print(f"raw_name = {raw_name}")
                    name = urllib.parse.unquote(raw_name)
                    print(f"name = {name}")
                    people_dict['name'] = name
                    break
        except Exception as ex:
            print(f"####### ERROR: Table Class vcard not found in {table_classes}:\n{ex}")

        # table_cls_str = "//table[@class='{}']/tbody/tr".format(table_cls)
        # print(f"table_cls_str: {table_cls_str}")
        # my_infobox_trs = response.xpath(table_cls_str)
        # print(f"my_infobox_trs: {my_infobox_trs}")

        people_dict['full_name'] = []
        people_dict['born'] = []
        people_dict['died'] = []
        people_dict['citizenship'] = []
        people_dict['known_for'] = []
        people_dict['schools'] = []
        people_dict['degrees'] = []
        people_dict['organizations'] = []
        people_dict['institutions'] = []
        people_dict['spouses'] = []
        people_dict['offspring'] = []
        people_dict['parents'] = []
        people_dict['relatives'] = []
        people_dict['house'] = []
        # people_dict['siblings'] = []
        # people_dict['cousin'] = []
        # people_dict['second_cousin'] = []
        people_dict['title'] = []
        people_dict['doctoral_advisor'] = []
        people_dict['fields'] = []
        people_dict['positions'] = []
        people_dict['occupation'] = []
        people_dict['employer'] = []
        people_dict['political_party'] = []
        people_dict['board_member'] = []
        people_dict['labels'] = []

        print(f"\n========  {people_dict['name']} ========")
        # print(response.xpath("//tr//th/a[@title='Alma mater' or @title='Education']/../following-sibling::td[@class='infobox-data']//text()[starts-with(., ' (') or starts-with(., ',')]/following-sibling::a[1]/text()")).getall()
        # print(response.xpath("//tr//*[starts-with(text(), 'Education') or starts-with(text(), 'Alma mater')]/following-sibling::td[@class='infobox-data']//text()[starts-with(., ' (') or starts-with(., ',')]/preceding-sibling::a[1]/text()").getall())
        # print(response.xpath("//tr//*[starts-with(text(), 'Education') or starts-with(text(), 'Alma mater')]/following-sibling::td[@class='infobox-data']//text()[starts-with(., ' (') or starts-with(., ',')]/following-sibling::a[1]/text()").getall())

        # headers = response.xpath("//table[@class='infobox vcard']//th[@class='infobox-header']")
        headers = response.css('.vcard').xpath("//th[@class='infobox-header']")
        people_dict = self.get_header_data(headers, people_dict)
        # labels = response.xpath("//table[@class ='infobox vcard'] // th[@ class ='infobox-label']")

        for tr in my_infobox_trs:
            if tr.xpath('th'):
                # th = tr.xpath('th')
                if tr.xpath('th/descendant-or-self::*/text()').get() not in [None, '']:
                # if tr.xpath('th/descendant-or-self::*/text()').get() not in [None, '']:
                    label_raw = tr.xpath('th/descendant-or-self::*/text()').get().lower()
                    label = label_raw.replace(NBSP, " ")
                    if label in EDUCATION_TYPE:
                        print(f"## {label} ##")
                        people_dict = self.get_education_data(tr, people_dict)
                    if 'field' in label:
                        print(f"## {label} ##")
                        fields = self.get_hrefs_text(tr)
                        people_dict['fields'] = fields
                    if label == 'doctoral advisor':
                        print(f"## {label} ##")
                        advisor = self.get_hrefs_text(tr)
                        people_dict['doctoral_advisor'] = advisor
                    if label in ['spouse(s)', 'spouses', 'spouse', 'partner', 'domestic partner']:
                        print(f"## {label} ##")
                        people_dict = self.get_spouse_data(tr, people_dict)
                    if label in ['parent', 'parent(s)', 'mother', 'father']:
                        print(f"## {label} ##")
                        people_dict = self.get_parents_data(tr, people_dict)
                    if label == 'children':
                        print(f"## {label} ##")
                        people_dict = self.get_offspring_data(tr, people_dict)
                        # all_offspring_dict.update(offspr_dict)
                    if label in ['born', 'date of birth']:
                        print(f'## {label} ##')
                        people_dict = self.get_died(tr, people_dict)
                    if label == 'died':
                        print(f'## {label} ##')
                        people_dict = self.get_born(tr, people_dict)
                    if label in ['relatives', 'family', 'members', 'house', 'relations']:
                        print(f'## {label} ##')
                        people_dict = self.get_relatives_data(tr, people_dict, label)
                    if label == 'occupation':
                        print(f'## {label} ##')
                        people_dict = self.get_occupation_data(tr, people_dict)
                    if label == 'citizenship':
                        print(f'## {label} ##')
                        employer = self.get_hrefs_text(tr)
                        people_dict['citizenship'] = employer
                    if label == 'political party':
                        print(f'## {label} ##')
                        party = self.get_hrefs_text(tr)
                        people_dict['political_party'] = party
                    if 'organization' in label:
                        print(f'## {label} ##')
                        organization = self.get_hrefs_text(tr)
                        people_dict['organizations'] = organization
                    if 'institution' in label:
                        print(f'## {label} ##')
                        institution = self.get_hrefs_text(tr)
                        people_dict['institutions'] = institution
                    if label == 'employer':
                        print(f'## {label} ##')
                        employer = self.get_hrefs_text(tr)
                        people_dict['employer'] = employer
                    if label == 'known for':
                        print(f'## {label} ##')
                        known_for = self.get_hrefs_text(tr)
                        people_dict['known_for'] = known_for
                    if label == 'title':
                        print(f'## {label} ##')
                        title = self.get_hrefs_text(tr)
                        people_dict['title'] = title
                    if label == 'board member of':
                        print(f'## {label} ##')
                        board_member = self.get_hrefs_text(tr)
                        people_dict['board_member'] = board_member
                    if label == 'labels':
                        print(f'## {label} ##')
                        labels = self.get_hrefs_text(tr)
                        people_dict['labels'] = labels
        yield people_dict

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

    def get_employer(self, tr):
        pass

    def get_hrefs_text(self, tr):
        if tr.xpath('td/a/@href'):
            my_text = tr.xpath('td//a/text()').getall()
        else:
            my_text = tr.xpath('td//text()').getall()

        # Remove values that are commas
        for text in my_text:
            if text in [', ', '', None]:
                my_text.remove(text)

        return my_text

    def get_header_data(self, my_headers, positions_dict):
        my_positions_list = []
        for header in my_headers:
            positions = header.xpath('.//text()').getall()
            position = "".join(positions)
            if position not in ["Personal details", "Signature", "Names"]:
                my_positions_list.append(position)

        positions_dict['positions'] = my_positions_list

        return positions_dict

    def get_born(self, tr, my_people_dict):
        if tr.xpath('td/text()').get():
            my_people_dict['died'] = tr.xpath('td/text()').get()

            return my_people_dict

    def get_died(self, tr, my_people_dict):
        if tr.xpath("//div[@class='nickname']/text()").get():
            my_people_dict['full_name'] = tr.xpath("//div[@class='nickname']/text()").get()

        if tr.xpath('//span[@class="bday"]/text()').get():
            my_people_dict['born'] = tr.xpath('//span[@class="bday"]/text()').get()
            # my_people_dict['born'] = dt.strptime(tr.xpath('//span[@class="bday"]/text()').get(), '%Y-%m-%d')
        elif tr.xpath('td/text()').get():
            my_people_dict['born'] = tr.xpath('td/text()').get()

        return my_people_dict

    def get_occupation_data(self, tr, my_people_dict):
        if tr.xpath('td//a/text()'):
            occupations = tr.xpath('td//a/text()').getall()
            my_people_dict['occupation'] = occupations
        elif tr.xpath('td/text()').get():
            my_people_dict['occupation'] = tr.xpath('td/text()').get()
        elif tr.xpath('td//li//text()'):
            my_people_dict['occupation'] = tr.xpath('td//li//text()').getall()
        # print(my_people_dict['occupation'])

        return my_people_dict

    def get_relatives_data(self, tr, my_people_dict, my_label):
        if tr.xpath('td//@href') not in [None, '']:
            relatives = tr.xpath('td//a/text()').getall()
        else:
            relatives = tr.xpath('td//text()').getall()

        # if my_label in ['house', 'family']:
        #         #     my_people_dict['house'] = relatives.strip(' family')
        #         #     return my_people_dict

        for relative in relatives:
            # my_people_dict['house'].append(relative.strip(' family'))
            if my_label in ['house', 'family'] or ' family' in relative.lower():
                my_people_dict['house'].append(relative.strip(' family'))
            else:
                my_people_dict['relatives'].append(relative)

        return my_people_dict

    def get_offspring_data(self, my_offspring_data, my_people_dict):
        if my_offspring_data.xpath('td//@href') not in [None, '']:
            offspring_href = my_offspring_data.xpath('td//@href').getall()
            print(offspring_href)
            for name in offspring_href:
                offspring_name = name.split('/')[-1].replace('_', ' ')
                if not offspring_name.startswith('#'):
                    my_people_dict['offspring'].append(offspring_name)
                    # wiki_page_name = wiki.get().split('/')[-1]
                    # my_offspring_dict[offspring_name] = wiki_page_name
                    # print(f"Offspring name: {offspring_name}")
                    # print(f"wiki: {wiki_page_name}")
            # my_people_dict['offspring'] = offspring_list
            # elif my_spouse_data.xpath('td/descendant-or-self::*/div/text()').get() not in [None, '']:
        elif my_offspring_data.xpath('td//text()') not in [None, '']:
            offspring_name = my_offspring_data.xpath('td//text()').getall()
            my_people_dict['offspring'] = offspring_name
            # print(f"Number of offspring: {offspring_name}")
        else:
            my_people_dict['offspring'] = None

        return my_people_dict

    def get_spouse_data(self, my_spouse_data, my_people_dict):
        spouse_list = []
        # if my_spouse_data.xpath('td/descendant-or-self::*/@href').get() not in [None, '']:
        if my_spouse_data.xpath('td//@href') not in [None, '']:
            spouse_href = my_spouse_data.xpath('td//@href').getall()
            # print(len(spouse_href))
            for wiki in spouse_href:
                spouse_name = wiki.split('/')[-1].replace('_', ' ')
                if not spouse_name.startswith('#'):
                    spouse_list.append(spouse_name)
                    # wiki_page_name = wiki.get().split('/')[-1]
                    # my_spouses_dict[spouse_name] = wiki_page_name
                    # print(spouse_name)
                    # print(f"wiki: {wiki_page_name}")
            my_people_dict['spouses'] = spouse_list
        # elif my_spouse_data.xpath('td/descendant-or-self::*/div/text()').get() not in [None, '']:
        elif my_spouse_data.xpath('td//text()').get() not in [None, '']:
            spouse_name = my_spouse_data.xpath('td//text()').getall()
            my_people_dict['spouses'] = spouse_name
            # print(spouse_name)
        else:
            my_people_dict['spouse'] += 'unknown'
            # print(f"Spouse cannot be retrieved from {my_spouse_data}")

        return my_people_dict

    def get_parents_data(self, my_parent_data, my_people_dict):
        parents_list = []
        if my_parent_data.xpath('td//@href') not in [None, '']:
            parent_href = my_parent_data.xpath('td//a/text()').getall()
            for wiki in parent_href:
                if not wiki.startswith('#'):
                    my_people_dict['parents'].append(wiki)
        elif my_parent_data.xpath('td//text()').get() not in [None, '']:
            parent_name = my_parent_data.xpath('td//text()').getall()
            my_people_dict['parents'].append(parent_name)
        else:
            my_people_dict['parents'].append(None)

        return my_people_dict

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
