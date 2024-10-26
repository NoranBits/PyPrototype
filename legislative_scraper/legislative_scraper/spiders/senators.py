import scrapy


class SenatorsSpider(scrapy.Spider):
    name = "senators"
    allowed_domains = ["sencanada.ca"]
    start_urls = ["https://sencanada.ca"]

    def parse(self, response):
        pass
