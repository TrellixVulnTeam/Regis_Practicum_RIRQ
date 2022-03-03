import scrapy
from collections import defaultdict

MY_URL_BASE = "en.wikipedia.org/wiki/"
DEFAULT_PROPS = ['born',
                 'education',
                 'alma_mater',
                 'spouse',
                 'parents',
                 'occupation',
                 'relatives']


class PeopleSpider(scrapy.Spider):
    name = 'people'
    allowed_domains = ['en.wikipedia.org/wiki/']
    start_urls = ['http://en.wikipedia.org/wiki/Robert_Reich']

    def parse(self, response):
        my_infobox_trs = response.xpath('//table[@class="infobox vcard"]/tbody/tr')
        # my_infobox_ths = my_infobox.xpath('th')
        # my_infobox_tds = my_infobox.xpath('td')
        people_dict = defaultdict()
        people_dict['name'] = my_infobox_trs[0].xpath('th/div/text()').get()

        for tr in my_infobox_trs:
            if tr.xpath('th'):
                if tr.xpath('th/text()').get() not in [None, '']:
                    title = tr.xpath('th/text()').get()
                    if tr.xpath('th/a/text()').get():
                        title2 = tr.xpath('th/a/text()').get()
                        title += title2
                    # print(title)
                    # people_dict[title] = None
                if tr.xpath('td'):
                    # print(tr.xpath('td/text()').get())
                    if tr.xpath('td/a/text()'):
                        val = tr.xpath('td/a/text()').get()
                        # print(tr.getAttribute('href'))
                    else:
                        val = tr.xpath('td/text()').get()
                    # print(val)
                    people_dict[title] = val
        print(people_dict)
