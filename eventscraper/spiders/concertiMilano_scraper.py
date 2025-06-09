import scrapy
from eventscraper.items import EventItem
from datetime import datetime
import re
from scrapy_playwright.page import PageMethod

class SpideconcertiSpider(scrapy.Spider):
    name = "concertiMilano_scraper"
    allowed_domains = ["teatro.it"]
    start_urls = [
        "https://www.teatro.it/spettacoli?region=301&prov=31&date-range=01%2F01%2F2019+-+31%2F12%2F2024"
    ]

    user_agent = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    )

    def start_requests(self):
        headers = {
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://www.teatro.it/',
        }
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                headers=headers,
                meta={
                    "playwright": True,
                    "playwright_context_kwargs": {
                        "user_agent": self.user_agent,
                        "locale": "it-IT",
                        "timezone_id": "Europe/Rome",
                        "java_script_enabled": True,
                    },
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", "div.show-list-item.single-slide", timeout=30000),
                    ],
                    "download_timeout": 60,
                },
                callback=self.parse
            )

    def parse(self, response):
        headers = {
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://www.teatro.it/',
        }
        self.logger.info(f"Scraping la pagina: {response.url}")

        next_page = response.css('a.page-link[rel="next"]::attr(href)').get()

        events = response.css('div.show-list-item')

        for event in events:
            event_url = event.css('div.card-footer a::attr(href)').get()
            if event_url:
                yield response.follow(
                    event_url,
                    headers=headers,
                    meta={
                        "playwright": True,
                        "playwright_context_kwargs": {
                            "user_agent": self.user_agent,
                            "locale": "it-IT",
                            "timezone_id": "Europe/Rome",
                            "java_script_enabled": True,
                        },
                        "playwright_page_methods": [
                            PageMethod("wait_for_selector", "h2.replica-title", timeout=30000),
                        ],
                        "download_timeout": 60,
                    },
                    callback=self.parse_event_page
                )

        if next_page:
            yield response.follow(
                next_page,
                headers=headers,
                meta={
                    "playwright": True,
                    "playwright_context_kwargs": {
                        "user_agent": self.user_agent,
                        "locale": "it-IT",
                        "timezone_id": "Europe/Rome",
                        "java_script_enabled": True,
                    },
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", "div.show-list-item.single-slide", timeout=30000),
                    ],
                    "download_timeout": 60,
                },
                callback=self.parse
            )

    def parse_event_page(self, response):
        event_item = EventItem()

        event_item['indirizzo'] = response.css('p.address .address-line1::text').get(default='').strip()
        event_item['titolo'] = response.css('h2.replica-title::text').get()
        event_item['categoria'] = "concerti"
        event_item['luogo'] = response.css('div.node--type-theater h4.fw-bold::text').get(default='').strip()

        raw_date = response.css('div.bg-black > div.row.mb-3.mt-n2 > div.col-5::text').get(default='').strip()

        def format_date(date_str):
            return datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d")

        match = re.search(r'Dal (\d{2}/\d{2}/\d{4})(?: al (\d{2}/\d{2}/\d{4}))?', raw_date)

        if match:
            start_date = match.group(1)
            end_date = match.group(2) if match.group(2) else start_date
            event_item['data_inizio'] = format_date(start_date)
            event_item['data_fine'] = format_date(end_date)
        else:
            event_item['data_inizio'] = ''
            event_item['data_fine'] = ''

        yield event_item