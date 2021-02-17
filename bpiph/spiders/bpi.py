import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from bpiph.items import Article


class BpiSpider(scrapy.Spider):
    name = 'bpi'
    start_urls = ['https://www.bpi.com.ph/announcements']

    def parse(self, response):
        links = response.xpath("//a[text()='Learn more']/@href").getall()
        yield from response.follow_all(links, self.parse_article)

    def parse_article(self, response):
        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        date = "".join(response.xpath('//div[@class="widget-text"]//em//text()').getall()[:-3])
        if date:
            date = datetime.strptime(date.strip(), '%B %d, %Y')
            date = date.strftime('%Y/%m/%d')

        content = response.xpath('//div[@class="split-container--area bp-area col-12 col-md-12 col-lg-8 order-2 '
                                 'order-lg-1 order-xl-1"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
