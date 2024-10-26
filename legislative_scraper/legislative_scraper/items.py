# legislative_scraper/items.py
import scrapy

class BillItem(scrapy.Item):
    number_code = scrapy.Field()
    parliament_number = scrapy.Field()
    session_number = scrapy.Field()
    bill_history = scrapy.Field()
    bill_stage = scrapy.Field()
    date = scrapy.Field()
    current_stage = scrapy.Field()
    voting_data = scrapy.Field()
    sponsor_id = scrapy.Field() 
    sponsor_full_name = scrapy.Field()
    sponsor_role_name = scrapy.Field() 
    division_number = scrapy.Field()
    

class BillDetailItem(scrapy.Item):
    bill_number = scrapy.Field()
    bill_number_prefix = scrapy.Field()
    parliament_number = scrapy.Field()
    session_number = scrapy.Field()
    title = scrapy.Field()
    short_title = scrapy.Field()
    bill_ref_number = scrapy.Field()
    bill_history = scrapy.Field()
    division_number = scrapy.Field()
    introduction = scrapy.Field()
    body = scrapy.Field()


class VoteItem(scrapy.Item):
    parliament_number = scrapy.Field()
    session_number = scrapy.Field()
    description = scrapy.Field()
    decision = scrapy.Field()
    related_bill_number = scrapy.Field()
    total_yeas = scrapy.Field()
    total_nays = scrapy.Field()
    total_abstain = scrapy.Field()
    vote_date = scrapy.Field()
    division_number = scrapy.Field()