# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html

from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
from datetime import datetime
from scrapy.exceptions import DropItem

class ZapposPipeline(object):

    def __init__(self):
        dispatcher.connect(self.spider_opened, signal=signals.spider_opened)
        dispatcher.connect(self.spider_closed, signal=signals.spider_closed)

    def spider_opened(self, spider):
        spider.started_on = datetime.now()

    def spider_closed(self, spider):
        work_time = datetime.now() - spider.started_on
        print "total crawl time is %s" % work_time

    def process_item(self, item, spider):
        return item
