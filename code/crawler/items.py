# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html
import sets
from scrapy.item import Item, Field

class CrawlerItem(Item):
    # define the fields for your item here like:
    # name = Field()
    product_name = Field()
    posted = Field()
    reviewer = Field()
    overall = Field()
    comfort = Field()
    style = Field()
    size = Field()
    arch= Field()
    width = Field()
    Description = Field()
    product_id = Field()
    url = Field()
    pass


