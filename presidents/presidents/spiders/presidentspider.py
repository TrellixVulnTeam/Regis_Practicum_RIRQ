import scrapy


class PresidentspiderSpider(scrapy.Spider):
    name = 'presidentspider'
    allowed_domains = ['en.wikipedia.org']
    start_urls = ['https://en.wikipedia.org/wiki/List_of_presidents_of_the_United_States']

    def parse(self, response):
        hrefs = response.xpath('//table[@class ="wikitable sortable"]/tbody//tr/td/b/a/@href').getall()
        # for href in hrefs:
        #     wiki_page = href.split('/')[-1]
        #     print(wiki_page)
        #     yield {
        #         'president_page': wiki_page
        #     }

        pres = response.xpath('//table[@class ="wikitable sortable"]/tbody//tr/td/b/a')
        for p in pres:
            print(p)
            print(p.xpath('../../td'))

        # vps = response.xpath('//table[@class="wikitable sortable jquery-tablesorter"]/tbody/tr/td[count(//table[@class="wikitable sortable jquery-tablesorter"]/tbody/tr/th[contains(., "Vice President")]/../th/td/a/@href) + 7]')
        # for vp in vps:
        #     print(vp)
        # trs = response.xpath('//table[@class ="wikitable sortable"]/tbody/tr')
        # for tr in trs:
        #     tds = tr.xpath('td["data-sort-value"]//a/@href').getall()
            # if len(tds) == 5:
            #     pres_wiki = tds[1:2]
            #     print(f"\nPresident: {pres_wiki}")
            #     vp7_wiki = tds[4:5]
            #     print(f"Veep: {vp7_wiki}")
            # elif len(tds) == 3:
            #     vp2_wiki = tds[1:2]
            #     print(vp2_wiki)
            # else:
            #     print(vp7_wiki)
            # print(f"\ntds - {tds}")
            # print(len(tds))
            # print(tds[1:2])
            # print(tds[-1:])
            # for td in tds:
            #     print(f"\ntd - {td}")
