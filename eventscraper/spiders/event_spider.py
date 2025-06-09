import scrapy
import html
from scrapy.selector import Selector
from datetime import datetime
import calendar
import requests
from eventscraper.items import EventItem


class EventScraper(scrapy.Spider):
    name = "event_scraper"

    # Specificare la città, l'anno, il mese o l'intervallo di mesi come argomenti della riga di comando
    # Se l'utente non specifica i mesi, verranno utilizzati gennaio e dicembre come valori predefiniti
    # Esempio: scrapy crawl EventScraper -a city=Event -a year=2023 -a month=10
    # Esempio: scrapy crawl EventScraper -a city=Event -a year=2023 -a start_month=3 -a end_month=5
    def __init__(self, city=None, year=None, month=None, start_month=None, end_month=None, *args, **kwargs):
        super(EventScraper, self).__init__(*args, **kwargs)

        if not city:
            self.logger.error("Errore: Devi specificare una città con l'argomento -a city=<nome_città>")
            raise ValueError("Devi specificare una città con l'argomento -a city=<nome_città>") 

        self.city = city.lower()

        # Se non viene specificato alcun anno, verrà utilizzato l'anno corrente come valore predefinito
        self.year = int(year) if year else datetime.today().year
        
        #Se l'utente ha specificato solo 'month', usa quel mese
        if month:
            self.start_month = self.end_month = int(month)
        else:
            # Se l'utente ha specificato 'start_month' e 'end_month', usali
            # Altrimenti, usa gennaio e dicembre come valori predefiniti
            self.start_month = int(start_month) if start_month else 1
            self.end_month = int(end_month) if end_month else 12

        self.start_urls = []
        for month in range(self.start_month, self.end_month + 1):
            last_day = calendar.monthrange(self.year, month)[1]
            start_date = f"{self.year}-{month:02d}-01"
            end_date = f"{self.year}-{month:02d}-{last_day}"
            url = f"https://www.{self.city}today.it/eventi/dal/{start_date}/al/{end_date}/"

            self.start_urls.append(url)

    def parse(self, response):
        
        events = response.css('article.c-card')
    
        for event in events:
            stelle = len(event.css('div.u-mt-small svg.c-rating.c-rating--filled').getall())
            categoria = event.css('span.c-card__kicker::text').get()

            if not categoria:
                raw_html = event.css('script[type="text/async-html"]::text').get()
                if raw_html:
                    decoded_html = html.unescape(raw_html)
                    inner_sel = Selector(text=decoded_html)
                    categoria = inner_sel.css('span.c-card__kicker::text').get()

            relative_url = event.xpath('.//header[@class="c-card__pull-down"]/a/@href').get()
            event_url = event_url = f"https://www.{self.city}today.it{relative_url}"
            yield response.follow(event_url, callback = self.parse_event_page, meta={'stelle': stelle, 'categoria': categoria}) 

        next_page = response.xpath('//a[svg/use[@*="#icon-chevron-right"]]/@href').get()
    
        if next_page is not None:
            if 'pag/' in next_page:
                next_page_url = next_page_url = f"https://www.{self.city}today.it{next_page}"
                
            yield response.follow(next_page_url, callback=self.parse)

    def parse_event_page(self, response):
        event_item = EventItem()

        stelle = response.meta.get('stelle', None)
        categoria = response.meta.get('categoria', None)

        event_item['titolo'] = response.css('h1.l-entry__title.u-heading-09::text').get()
        event_item['luogo'] = response.css('a.o-link-primary.u-label-04.u-py-xsmall::text').get()
        event_item['indirizzo'] = response.xpath('normalize-space(//a[@href="#map"]/text())').get()
        event_item['data_inizio'] = response.xpath('//span[contains(text(), "Dal")]/span/text()').get()
        event_item['data_fine'] = response.xpath('//span[contains(text(), " al ")]/span/text()').get()
        event_item['orario'] = response.css('span.u-label-011::text').get()
        if event_item['data_fine'] is None or event_item['data_fine'].strip() == "":
            event_item['data_fine'] = event_item['data_inizio']
        event_item['prezzo'] = response.xpath('//span[contains(text(), "Prezzo")]/following-sibling::span/text()').get()
        event_item['categoria'] = categoria
        event_item['url'] = response.url
        event_item['stelle'] = stelle

        #descrizione_paragrafi = response.css('section.c-entry p *::text, div.c-entry.u-p-small p *::text').getall()

        #descrizione_filtrata = [p for p in descrizione_paragrafi if not p.startswith('{') and not any(keyword in p.lower() for keyword in ["video", "image"])]
        #descrizione = " ".join(descrizione_filtrata).strip()
        #event_item['descrizione'] = descrizione

        yield event_item