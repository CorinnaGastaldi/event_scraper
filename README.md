Questo progetto è uno scraper basato su Scrapy progettato per raccogliere informazioni sugli eventi culturali (come concerti e spettacoli teatrali) in Italia. 
Supporta l’estrazione da due siti principali:
- Teatro.it – eventi teatrali e concerti
- cityToday.it – eventi locali specifici per città italiane

Tecnologie utilizzate:
- Scrapy per lo scraping
- Playwright per il rendering di pagine dinamiche
- scrapy-playwright per lo scraping su teatro.it con eventi dinamici

Spider disponibili:
- **concertiMilano_scraper**: estrae concerti dalla provincia di Milano su Teatro.it tra il 2019 e il 2024
- **event_scraper**: scraper dinamico per il sito milano.today.it (e siti simili). Può essere configurato da linea di comando per:
Città (es. milano), Anno (year), Mese (month) o intervallo (start_month, end_month)

Clona la repository:
- git clone https://github.com/CorinnaGastaldi/event_scraper.git
- cd event_scraper
  
Ambiente virtuale:
- python -m venv env
- source env/bin/activate  # su Windows: env\Scripts\activate

Dipendenze:
- pip install -r requirements.txt
- python -m playwright install

Esecuzione degli spider:
- Spider concertiMilano: **scrapy crawl concertiMilano_scraper -o concerti.csv**
- Spider configurabile: **scrapy crawl event_scraper -a city=milano -a year=2024 -a month=6 -o eventi.csv**
- Spider con intervallo di tempo: **scrapy crawl event_scraper -a city=milano -a year=2024 -a start_month=5 -a end_month=7 -o eventi.csv**




