import scrapy
import xml.etree.ElementTree as ET
from scrapy.http import Request
from legislative_scraper.items import BillItem, BillDetailItem

BASE_URL = "https://www.parl.ca"
BILLS_LIST_URL = f"{BASE_URL}/legisinfo/en/bills/xml?parlsession={{parliament}}-{{session}}"
BILL_DATA_URL = f"{BASE_URL}/LegisInfo/en/bill/{{parliament}}-{{session}}/{{bill_number}}/xml"
BILL_DETAILS_URL = f"{BASE_URL}/Content/Bills/{{parliament}}{{session}}/{{bill_type}}/{{bill_number}}/{{bill_number}}_{{count}}/{{bill_number}}_E.xml"
BILL_VOTES_URL = f"https://www.ourcommons.ca/Members/en/votes/xml?parlSession={{parliament}}/{{session}}"
class BillSessionSpider(scrapy.Spider):
    name = "bill_session"
    allowed_domains = ["parl.ca", "ourcommons.ca"]
    max_parliaments = 1000  # Optional limit for parliaments
    max_sessions = 4  # Optional limit for sessions
    max_counts = 100  # Optional limit for counts

    def start_requests(self):
        parliament = 35  # Starting from parliament 35
        while parliament <= self.max_parliaments:
            session = 1
            while session <= self.max_sessions:
                url = BILLS_LIST_URL.format(parliament=parliament, session=session)
                self.logger.info(f"Requesting bills list URL: {url}")
                yield Request(
                    url,
                    callback=self.parse_bills_list,
                    cb_kwargs={"parliament": parliament, "session": session},
                    errback=lambda failure, p=parliament, s=session: self.handle_error(failure, p, s),
                    meta={
                        'dont_redirect': True,
                        'handle_httpstatus_list': [200, 301, 302, 404]
                    }
                )
                session += 1
            parliament += 1

    def handle_error(self, failure, parliament, session):
        response = failure.value.response
        if response.status in [404, 301, 302]:
            self.logger.info(f"Received status {response.status} for Parliament {parliament}, Session {session}. No further requests for this session.")
        else:
            self.logger.error(f"Request failed for URL: {response.url} with status {response.status}")

    def parse_bills_list(self, response, parliament, session):
        if response.status in [301, 302, 404]:
            self.logger.info(f"Received status {response.status} for Parliament {parliament}, Session {session}. Skipping.")
            return

        try:
            root = ET.fromstring(response.text)
            bills = root.findall(".//Bill")
            if not bills:
                self.logger.info(f"No bills found for Parliament {parliament}, Session {session}.")
                return

            for bill in bills:
                bill_number = bill.findtext("NumberCode")
                if not bill_number:
                    self.logger.warning(f"No bill number found for a bill in Parliament {parliament}, Session {session}.")
                    continue

                # Prepare bill data
                bill_data = {
                    'bill_number': bill_number,
                    'parliament_number': parliament,
                    'session_number': session,
                    'bill_stage': bill.findtext("LatestCompletedBillStageName"),
                    'bill_stage_date': bill.findtext("LatestCompletedBillStageDateTime"),
                    'sponsor_id': bill.findtext("SponsorPersonId"),
                    'sponsor_name': bill.findtext("SponsorPersonName"),
                    'sponsor_role': bill.findtext("SponsorAffiliationRoleName")
                }

                # Generate the bill data URL
                bill_data_url = BILL_DATA_URL.format(
                    parliament=parliament,
                    session=session,
                    bill_number=bill_number
                )
                self.logger.info(f"Generated Bill Data URL: {bill_data_url}")
                yield Request(
                    bill_data_url,
                    callback=self.parse_bill_data,
                    cb_kwargs=bill_data,
                    errback=lambda failure: self.handle_error(failure, parliament, session),
                    meta={
                        'dont_redirect': True,
                        'handle_httpstatus_list': [200, 301, 302, 404]
                    }
                )

                # Generate initial bill details requests
                yield from self.generate_bill_details_requests(bill_data)

        except ET.ParseError as e:
            self.logger.error(f"Failed to parse XML for Parliament {parliament}, Session {session}: {e}")
            self.logger.debug(f"Response content: {response.text}")

    def generate_bill_details_requests(self, bill_data):
        # Extract variables from bill_data
        parliament = bill_data['parliament_number']
        session = bill_data['session_number']
        bill_number = bill_data['bill_number']

        for bill_type in ['Government', 'Private']:
            count = 1  # Start with the first version
            bill_details_url = BILL_DETAILS_URL.format(
                parliament=parliament,
                session=session,
                bill_type=bill_type,
                bill_number=bill_number,
                count=count
            )
            self.logger.info(f"Generated Bill Details URL: {bill_details_url}")
            request_meta = {
                'bill_data': bill_data,
                'bill_type': bill_type,
                'count': count,
                'dont_redirect': True,
                'handle_httpstatus_list': [200, 301, 302, 404]
            }
            yield Request(
                bill_details_url,
                callback=self.parse_bill_details,
                meta=request_meta,
                errback=self.handle_bill_details_error
            )

    def parse_bill_data(self, response, **bill_data):
        if response.status in [301, 302, 404]:
            self.logger.info(f"Received status {response.status} for Bill Data URL: {response.url}. Skipping.")
            return

        try:
            root = ET.fromstring(response.text)

            # Extract the bill stage and sponsor details
            bill_stage = root.findtext(".//LatestCompletedBillStageName")
            bill_stage_date = root.findtext(".//LatestCompletedBillStageDateTime")
            sponsor_id = root.findtext(".//SponsorPersonId")
            sponsor_name = root.findtext(".//SponsorPersonName")
            sponsor_role = root.findtext(".//SponsorAffiliationTitle") 


            bill_item = BillItem(
                bill_number=bill_data['bill_number'],
                parliament_number=bill_data['parliament_number'],
                session_number=bill_data['session_number'],
                sponsor_id=sponsor_id,
                sponsor_name=sponsor_name,
                sponsor_role=sponsor_role,
                bill_stage=bill_stage,
                bill_stage_date=bill_stage_date
            )

            self.logger.info(f"Extracted data for Bill: {bill_item['bill_number']}")
            yield bill_item

        except ET.ParseError as e:
            self.logger.error(f"Failed to parse XML for Bill Data: {e}")
            self.logger.debug(f"Response content: {response.text}")

    def parse_bill_details(self, response):
        bill_data = response.meta['bill_data']
        bill_type = response.meta['bill_type']
        count = response.meta['count']

        if response.status in [301, 302, 404]:
            self.logger.info(f"Received status {response.status} for Bill Details URL: {response.url}. No further requests for this bill version.")
            return  # Do not generate further requests

        try:
            root = ET.fromstring(response.text)
            identification = root.find(".//Identification")
            if identification is not None:
                bill_detail_item = BillDetailItem(
                    bill_number=identification.findtext("BillNumber"),
                    session_number=identification.findtext("Parliament/Session"),
                    title=identification.findtext("LongTitle"),
                    short_title=identification.findtext("ShortTitle"),
                    sponsor=identification.findtext("BillSponsor"),
                    bill_ref_number=identification.findtext("BillRefNumber"),
                    bill_history=ET.tostring(root.find(".//BillHistory"), encoding='unicode') if root.find(".//BillHistory") else None,
                    introduction=ET.tostring(root.find(".//Introduction"), encoding='unicode') if root.find(".//Introduction") else None,
                    body=ET.tostring(root.find(".//Body"), encoding='unicode') if root.find(".//Body") else None,
                )
                self.logger.info(f"Extracted details for Bill: {bill_detail_item['bill_number']}")
                yield bill_detail_item
            else:
                self.logger.warning(f"Identification section not found for URL: {response.url}")
        except ET.ParseError as e:
            self.logger.error(f"Failed to parse XML for Bill Details {response.url}: {e}")
            self.logger.debug(f"Response content: {response.text}")
            return  # Do not generate further requests on parse error

        # Generate the next bill details request if within max_counts limit
        next_count = count + 1
        if next_count <= self.max_counts:
            parliament = bill_data['parliament_number']
            session = bill_data['session_number']
            bill_number = bill_data['bill_number']

            next_bill_details_url = BILL_DETAILS_URL.format(
                parliament=parliament,
                session=session,
                bill_type=bill_type,
                bill_number=bill_number,
                count=next_count
            )

            # Before generating the next request, check if the current response was valid
            # If not, do not generate further requests
            if response.status == 200:
                self.logger.info(f"Generated next Bill Details URL: {next_bill_details_url}")
                request_meta = {
                    'bill_data': bill_data,
                    'bill_type': bill_type,
                    'count': next_count,
                    'dont_redirect': True,
                    'handle_httpstatus_list': [200, 301, 302, 404]
                }
                yield Request(
                    next_bill_details_url,
                    callback=self.parse_bill_details,
                    meta=request_meta,
                    errback=self.handle_bill_details_error
                )
            else:
                self.logger.info(f"Stopping further requests for Bill {bill_number}, Bill Type {bill_type}, due to status {response.status}")
        else:
            self.logger.info(f"Reached max counts for Bill {bill_number}, Bill Type {bill_type}")

    def handle_bill_details_error(self, failure):
        response = failure.value.response
        bill_data = response.meta['bill_data']
        bill_type = response.meta['bill_type']
        count = response.meta['count']
        bill_number = bill_data['bill_number']

        if response.status in [404, 301, 302]:
            self.logger.info(f"Received status {response.status} for Bill Details URL: {response.url}. No further requests for this bill version.")
        else:
            self.logger.error(f"Request failed for URL: {response.url} with status {response.status}")

        # Do not generate further requests since an error occurred