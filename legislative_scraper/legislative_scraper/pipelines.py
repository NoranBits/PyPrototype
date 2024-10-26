# legislative_scraper/pipelines.py
import psycopg2
from legislative_scraper.items import BillItem, BillDetailItem, VoteItem
import logging

class PostgresPipeline:
    def open_spider(self, spider):
        self.connection = psycopg2.connect(
            dbname='legislative_data',
            user='postgres',
            password='password',
            host='localhost',
            port='5432'
        )
        self.cursor = self.connection.cursor()
        logging.info("Database connection opened.")

    def close_spider(self, spider):
        self.cursor.close()
        self.connection.close()
        logging.info("Database connection closed.")

    def process_item(self, item, spider):
        try:
            if isinstance(item, BillItem):
                self.cursor.execute('''
                    INSERT INTO bills (number_code, parliament_number, session_number, bill_history, latest_completed_stage, division_number, bill_stage, date, current_stage)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (number_code, parliament_number, session_number) DO NOTHING
                ''', (
                    item['number_code'],
                    item['parliament_number'],
                    item['session_number'],
                    item['bill_history'],
                    item['latest_completed_stage'],
                    item['division_number'],
                    item['bill_stage'],
                    item['date'],
                    item['current_stage']
                ))
            elif isinstance(item, BillDetailItem):
                self.cursor.execute('''
                    INSERT INTO bill_details (bill_number, bill_number_prefix, parliament_number, session_number, title, short_title, sponsor, bill_ref_number, bill_history, introduction, body, division_number)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (bill_number, parliament_number, session_number) DO NOTHING
                ''', (
                    item['bill_number'],
                    item['bill_number_prefix'],
                    item['parliament_number'],
                    item['session_number'],
                    item['title'],
                    item['short_title'],
                    item['sponsor'],
                    item['bill_ref_number'],
                    item['bill_history'],
                    item['introduction'],
                    item['body'],
                    item['division_number']
                ))
            elif isinstance(item, VoteItem):
                self.cursor.execute('''
                    INSERT INTO bill_votes (parliament_number, session_number, description, decision, related_bill_number, total_yeas, total_nays, total_abstain, vote_date, division_number)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (related_bill_number, parliament_number, session_number, vote_date) DO NOTHING
                ''', (
                    item['parliament_number'],
                    item['session_number'],
                    item['description'],
                    item['decision'],
                    item['related_bill_number'],
                    item['total_yeas'],
                    item['total_nays'],
                    item['total_abstain'],
                    item['vote_date'],
                    item['division_number']
                ))
            self.connection.commit()
        except psycopg2.Error as e:
            logging.error(f"Error processing item: {e}")
            self.connection.rollback()
        return item