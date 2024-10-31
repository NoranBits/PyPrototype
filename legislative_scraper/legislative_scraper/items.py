# legislative_scraper/items.py
import scrapy

class BillItem(scrapy.Item):
    bill_number = scrapy.Field()
    parliament_number = scrapy.Field()
    session_number = scrapy.Field()
    bill_stage = scrapy.Field()
    bill_stage_date = scrapy.Field()
    sponsor_id = scrapy.Field()
    sponsor_name = scrapy.Field()
    sponsor_role = scrapy.Field()
    

class BillDetailItem(scrapy.Item):
    bill_number = scrapy.Field()
    parliament_number = scrapy.Field()
    session_number = scrapy.Field()
    title = scrapy.Field()
    short_title = scrapy.Field()
    bill_ref_number = scrapy.Field()
    sponsor = scrapy.Field()
    bill_history = scrapy.Field()
    introduction = scrapy.Field()
    body = scrapy.Field()


class VoteItem(scrapy.Item):
    bill_number = scrapy.Field()
    parliament_number = scrapy.Field()
    session_number = scrapy.Field()
    description = scrapy.Field()
    decision = scrapy.Field()
    total_yeas = scrapy.Field()
    total_nays = scrapy.Field()
    total_abstain = scrapy.Field()
    total_paired = scrapy.Field()
    vote_date = scrapy.Field()
    division_number = scrapy.Field()