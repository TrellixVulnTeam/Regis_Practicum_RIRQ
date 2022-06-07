import scrapy
import csv
from collections import defaultdict


def gen_urls(my_years):
    my_urls = []

    for year in my_years:
        my_urls.append(f'https://bildercrawler/meetings/meeting-{year}/participants-{year}')

    return my_urls


class BilderbergSpider(scrapy.Spider):
    name = 'bilders'
    years = ['2019', '2018', '2017', '2016']
    allowed_domains = ['bildercrawler/']
    start_urls = gen_urls(years)

    def parse(self, response):
        # bilders_selector = response.xpath('//div[@class="text"]/p[2]//br/following-sibling::text()')
        bilders_selector = response.xpath('//div[@class="text"]/p[*]//br')
        bilders_list = self.build_bilders_list(bilders_selector)
        people_dict = self.get_bilderbergers_data(bilders_list)

        yield people_dict

    def build_bilders_list(self, my_selector):
        my_list = []

        for name in my_selector:
            name = name.xpath('following-sibling::text()').get()
            pos_org = name.xpath('following-sibling::*[1]/text()').get()
            my_list.append([name.strip(), pos_org])

        return my_list

    def get_bilderbergers_data(self, raw_list):
        bilders_dict = defaultdict()
        bilders_list = []

        for i in raw_list:
            if list(i)[0] != None and list(i)[1] != None:
                name_country = list(i)[0].split(' (')
                first_name = name_country[0].split(',')[1]
                last_name = name_country[0].split(',')[0]
                name = f"{first_name} {last_name}"
                country = name_country[1].replace(')', '')
                country = country.replace(',', '')
                pos_org = list(i)[1].split(',')
                position = pos_org[0]
                if len(pos_org) > 1:
                    organization = pos_org[1]
                else:
                    organization = ''
                bilders_list.append([name, country, position, organization])
                bilders_dict.update({'name': name,
                                     'citizenship': country,
                                     'position': position,
                                     'organization': organization})

        with open('builders_native.csv', 'w', newline='') as f:
            csv_writer = csv.DictWriter(f, fieldnames=['name', 'citizenship', 'position', 'organization'])
            csv_writer.writeheader()
            for b in bilders_list:
                csv_writer.writerow({'name': b[0], 'citizenship': b[1], 'position': b[2], 'organization': b[3]})

        return bilders_dict
