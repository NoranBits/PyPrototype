import psycopg2
from legislative_scraper.items import BillItem, BillDetailItem
from scrapy.exceptions import NotConfigured
import os
from dotenv import load_dotenv

class PostgresPipeline:
    def open_spider(self, spider):
        # Load environment variables
        load_dotenv()
        try:
            self.connection = psycopg2.connect(
                host=os.getenv('DATABASE_HOST'),
                port=int(os.getenv('DATABASE_PORT')),
                user=os.getenv('DATABASE_USER'),
                password=os.getenv('DATABASE_PASSWORD'),
                dbname=os.getenv('DATABASE_NAME')
            )
            self.cursor = self.connection.cursor()
        except Exception as e:
            spider.logger.error(f"Failed to connect to database: {e}")
            raise NotConfigured("Database connection failed")

    def close_spider(self, spider):
        if hasattr(self, 'cursor'):
            self.cursor.close()
        if hasattr(self, 'connection'):
            self.connection.close()

    def process_item(self, item, spider):
        if isinstance(item, BillItem):
            try:
                # Safely convert sponsor_id to integer or set to None
                sponsor_id_raw = item.get('sponsor_id')
                sponsor_id = int(sponsor_id_raw) if sponsor_id_raw and sponsor_id_raw.strip().isdigit() else None

                values = (
                    item.get('bill_number'),
                    item.get('parliament_number'),
                    item.get('session_number'),
                    item.get('bill_stage') or None,
                    item.get('bill_stage_date') or None,
                    sponsor_id,
                    item.get('sponsor_name') or None,
                    item.get('sponsor_role') or None
                )

                # Log the values for debugging
                spider.logger.debug(f"Inserting BillItem with values: {values}")

                # Execute the SQL statement
                self.cursor.execute('''
                    INSERT INTO bills (
                        bill_number, parliament_number, session_number, bill_stage, bill_stage_date,
                        sponsor_id, sponsor_name, sponsor_role
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (bill_number, parliament_number, session_number) DO NOTHING
                ''', values)

                self.connection.commit()
            except Exception as e:
                # Rollback the transaction to reset the database state
                self.connection.rollback()
                spider.logger.error(f"Error inserting BillItem: {e}")
                spider.logger.debug(f"Values attempted: {values}")
        elif isinstance(item, BillDetailItem):
            try:
                values = (
                    item.get('bill_number'),
                    item.get('parliament_number'),
                    item.get('session_number'),
                    item.get('title'),
                    item.get('short_title'),
                    item.get('sponsor'),
                    item.get('bill_ref_number'),
                    item.get('bill_history'),
                    item.get('introduction'),
                    item.get('body'),
                )

                # Execute the SQL statement
                self.cursor.execute('''
                    INSERT INTO bill_details (
                        bill_number, parliament_number, session_number, title, short_title, sponsor,
                        bill_ref_number, bill_history, introduction, body
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (bill_number, parliament_number, session_number) DO NOTHING
                ''', values)
                self.connection.commit()
            except Exception as e:
                spider.logger.error(f"Error inserting BillDetailItem: {e}")
                spider.logger.debug(f"Values attempted: {values}")
                raise e  # Optionally re-raise the exception
        return item