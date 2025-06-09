# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import scrapy
    

class EventItem(scrapy.Item):
    # define the fields for your item here like:
    titolo = scrapy.Field()
    luogo = scrapy.Field()
    indirizzo = scrapy.Field()
    prezzo = scrapy.Field()
    stelle = scrapy.Field()
    categoria = scrapy.Field()
    url = scrapy.Field()
    orario = scrapy.Field()
    data_inizio = scrapy.Field()
    data_fine = scrapy.Field()
    
    
