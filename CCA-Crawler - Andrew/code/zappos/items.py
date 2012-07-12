# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

class ZapposItem(Item):
    product_name = Field()
    product_id = Field()
    posted = Field()
    reviewer = Field()
    location = Field()
    overall = Field()
    comfort = Field()
    style = Field()
    size = Field()
    arch = Field()
    width = Field()
    description = Field()
    url = Field()
