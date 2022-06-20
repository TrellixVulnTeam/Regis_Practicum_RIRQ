import scrapy
from scrapy.crawler import CrawlerProcess


class YglSpider(scrapy.Spider):
    name = 'leaders'

    def start_requests(self):
        yield scrapy.Request('https://www.younggloballeaders.org/community')

    def parse(self, response):
        num_pages = response.xpath('/html/body/div[1]/section/article/section/section/div/div/div/nav/div/span[6]/a/text()')
        last_page = int(num_pages)
        person_details = response.xpath('/html/body//div/section/article/section/section/div/div/div//article/div//div[@class="person-details"]')

        for person in person_details:
            name = person.xpath('h3/text()').get()
            all_details = person.xpath('p/text()').get()
            details = all_details.split(',')

            if len(details) == 3:
                title = details[0]
                institution = details[1]
                country = details[2]
            elif len(details) > 3:
                title = ','.join(details[0:-2])
                institution = details[-2]
                country = details[-1]
            else:
                title = 'NA'
                institution = 'NA'
                country = 'NA'

            yield {
                'name': name,
                'title': title,
                'institution': institution,
                'country': country
            }

        for x in range(2, last_page):
            yield(scrapy.Request(f'https://www.younggloballeaders.org/community?page={x}', callback=self.parse))


process = CrawlerProcess(settings={
    'FEED_URI': 'wikicrawler/global_leaders.csv',
    'FEED_FORMAT': 'csv'
})

process.crawl(YglSpider)
process.start()
