from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from crawler.items import CrawlerItem
from scrapy.contrib.loader import XPathItemLoader
from scrapy import log
from time import sleep
import sets
import re

from scrapy.http import Request

class mySpider(CrawlSpider):
    name = "zappos.com"
    allowed_domains = ["zappos.com"]
    start_urls = [
        "http://www.zappos.com"
    ]
    visited = set()
    fullLinksScan = set()
    rules = (
        # Extract links matching 'item.php' and parse them with the spider's method parse_depth1
        Rule(SgmlLinkExtractor(allow=('(/shoes|/clothing)$')) ,callback = 'parse_depth1'),
    )
    
    def parse_depth1(self, response):
        #self.log("This is the link i have collected : %s !" % response.url)
        hxs = HtmlXPathSelector(response)
        global visited
        global fullLinksScan
        global additionalcomments
        fullLinksScan = set()
        visited = set()
        additionalcomments = set()
        for link in hxs.select('//a[contains(.,"Women\'s Shoes")]'):
            print(" Root url : %s " % link.select('@href').extract()[0])
            yield Request("http://www.zappos.com" + link.select('@href').extract()[0], callback = self.parse_depth2)

    def parse_depth2(self, response):
        global fullLinksScan
        global visited
        hxs = HtmlXPathSelector(response)
        query = "//a[contains(@href,'/women-') and not(contains(@href,'/women-shoes'))]"
        for link in hxs.select(query):
            print("First Child url : %s " % link.select('@href').extract()[0])
            yield Request("http://www.zappos.com" + link.select('@href').extract()[0], callback = self.build_links)

    def build_links (self, response):
        global fullLinksScan
        hxs = HtmlXPathSelector(response)
        lastpage = hxs.select(".//span[contains(@class, 'last')][1]/a[1]/text()").extract()
        fullLinksScan.add(response.url)
        if (len(lastpage) != 0):
            lastpage = int(lastpage.pop())
            page_url = hxs.select(".//div[contains(@class, 'pagination')][1]/a[1]")
            page_url = page_url.select('@href').extract()[0]
            for index in range(1, lastpage):
                page_url = re.sub("(?<=p\=)\d*", str(index), page_url)
                fullLinksScan.add("http://www.zappos.com" + page_url)
                print("Adding url to fullLinksScan %s :" % page_url)
        print("length of len(fullLinksScan) is %s " % len(fullLinksScan))
        for i in range(1, len(fullLinksScan)):
            if (len(fullLinksScan) != 0):
                new_url = str(fullLinksScan.pop()) 
                print("Parsing the url of fullLinksScan %s :" % new_url)
                yield Request(new_url, callback = self.parse_depth3)
        
    def parse_depth3(self, response):
        global fullLinksScan
        global visited
        global additionalcomments
        ur=""
        hxs = HtmlXPathSelector(response)
        query = "//a[contains(@href,'/product')]"
        for link in hxs.select(query):
            if (link not in visited):
                visited.add("http://www.zappos.com" + link.select('@href').extract()[0])
                print("adding url to visited %s :" % link.select('@href').extract()[0])
        while (len(visited) > 0):
            ur = str(visited.pop())
            print ("Going to final producr: %s" % ur)
            yield Request(ur, callback = self.parse_final2)
        while(len(additionalcomments)):
            yield Request (str(additionalcomments.pop()), callback = self.parse_final5)

    def parseadditionalcomments(self, hxs, response):
        global additionalcomments
        valuefile = hxs.select('//div[contains(@class, "additional")]/a')
        if (len(valuefile) == 2):
            #yield Request ("http://www.zappos.com" + str(valuefile[1].select('@href').extract()[0]), callback=self.collectadditionallinks)
            print("printing: %s" % valuefile[1].select('./text()'))
            additionalReviews = int(re.search("(\d+)", str(valuefile[1].select('./text()'))).group(1))
            productId = re.search("(\d+)", str(response.url)).group(1)
            print("additionalReviews %d" % additionalReviews)
            if (additionalReviews != 0):
                maxPagesAdditional = additionalReviews / 25
                print("maxPagesAdditional %d" % maxPagesAdditional)
                for i in range(0, (maxPagesAdditional + 1)):
                    if (maxPagesAdditional > 20):
                        pass
                    else:
                        pageno = i + 1
                        if (i == maxPagesAdditional):
                            if(additionalReviews % 25 == 0):
                                pass
                            else:
                                print("http://www.zappos.com/product/review/" + str(productId) + "/page/" + str(pageno) +"/start/20")
                                additionalcomments.add("http://www.zappos.com/product/review/" + str(productId) + "/page/" + str(pageno) +"/start/20")
                        else:
                            print("http://www.zappos.com/product/review/" + str(productId) + "/page/" + str(pageno) +"/start/20")
                            additionalcomments.add("http://www.zappos.com/product/review/" + str(productId) + "/page/" + str(pageno) +"/start/20")
        return

    def parse_final2(self, response):
        global visited
        hxs = HtmlXPathSelector(response)
        sites = hxs.select('//div[contains(@class, "review")]')
        if ( len(hxs.select('//div[contains(@class, "additional")]')) != 0):
            self.parseadditionalcomments(hxs, response)
        for site in sites:
                print ("Parsing the product")
                if (len(site.select('.//*[contains(@class, "info")]/strong[.="Posted:"]/following-sibling::text()[1]')) != 0):
                    item = CrawlerItem()
                    if (site.select('//*[contains(@class, "prName")]/*/text()')):
                        item['product_name'] = (site.select('//*[contains(@class, "prName")]/*/text()').extract() + site.select ('//*[contains(@class, "prName")]/text()').extract())
                    else:
                        item['product_name'] = site.select ('//*[contains(@class, "prName")]/text()').extract()
                    item['product_name']=item['product_name'].pop();
                    item['style'] = site.select('.//*[contains(@class, "info")]/span[3]/span[1]/@class').extract()
                    if (len(item['style']) != 0):
                        item['style'] = re.search("(\d+)", str(item['style'].pop())).group(1)
                    else:
                        item['style'] = '';
                    item['product_id'] = site.select('//*[contains(@class, "sku")]/text()').extract()[0]
                    #item['product_id'] = item['product_id'].pop();
                    item['posted'] = site.select('.//*[contains(@class, "info")]/strong[.="Posted:"]/following-sibling::text()[1]').extract()
                    item['posted']=item['posted'].pop();
                    item['reviewer'] = site.select('.//*[contains(@class, "info")]/strong[.="Reviewer:"]/following-sibling::text()[1]').extract()
                    item['reviewer']=item['reviewer'].pop();
                    item['overall'] = site.select('.//*[contains(@class, "info")]/span[1]/span[1]/@class').extract()
                    if (len(item['overall']) != 0):
                        item['overall'] = re.search("(\d+)", str(item['overall'].pop())).group(1)
                    else:
                        item['overall'] = ''
                    item['comfort'] = site.select('.//*[contains(@class, "info")]/span[2]/span[1]/@class').extract()
                    if (len(item['comfort']) != 0):
                        item['comfort']=re.search("(\d+)", str(item['comfort'].pop())).group(1)
                    else:
                        item['comfort']= ''
                    item['size'] = site.select('.//*[contains(@class, "feel")]/span[1]/strong[.="Shoe Size:"]/following-sibling::text()[1]').extract()
                    if (len(item['size']) != 0):
                        item['size'] = item['size'].pop();
                    else:
                        item['size'] = ''
                    item['arch'] = site.select('.//*[contains(@class, "feel")]/span[2]/strong[.="Shoe Arch:"]/following-sibling::text()[1]').extract()
                    if (len(item['arch']) != 0):
                        item['arch'] = item['arch'].pop();
                    else:
                        item['arch'] = ''
                    item['width'] = site.select('.//*[contains(@class, "feel")]/span[3]/strong[.="Shoe Width:"]/following-sibling::text()[1]').extract()
                    if ( len(item['width']) != 0 ):
                        item['width'] = item['width'].pop();
                    else:
                        item['width']=''
                    summary = site.select('.//*[contains(@class, "summary")]/p/text()').extract()
                    #summary = site.select('.//*[contains(@class, "summary")]/p').extract()
                    #print("Initial Node val %s" % site.select('.//*[contains(@class, "summary")]/p'))
                    #for i,node in enumerate(site.select('.//*[contains(@class, "summary")]/p')):
                    #    print("Printing")
                    #    print(i, node)
                    description = ""
                    while (len(summary) != 0):
                        description = description + summary.pop(0).encode('utf-8')
                    description = str(description)
                    item['Description'] = description
                    item['url'] = response.url
                    print("Finished parsing the product %s" % response.url)
                    yield item

    def parse_final5(self, response):
        global visited
        hxs = HtmlXPathSelector(response)
        sites = hxs.select('//div[contains(@class, "review")]')
        for site in sites:
                print ("Parsing the product")
                if (len(site.select('.//*[contains(@class, "info")]/strong[.="Posted:"]/following-sibling::text()[1]')) != 0):
                    item = CrawlerItem()
                    item['style'] = site.select('.//*[contains(@class, "info")]/span[3]/span[1]/@class').extract()
                    if (len(item['style']) != 0):
                        item['style'] = re.search("(\d+)", str(item['style'].pop())).group(1)
                    else:
                        item['style'] = '';
                    item['product_id'] = re.search("(\d+)", str(response.url)).group(1)
                    #item['product_id'] = item['product_id'].pop();
                    item['posted'] = site.select('.//*[contains(@class, "info")]/strong[.="Posted:"]/following-sibling::text()[1]').extract()
                    item['posted']=item['posted'].pop();
                    item['reviewer'] = site.select('.//*[contains(@class, "info")]/strong[.="Reviewer:"]/following-sibling::text()[1]').extract()
                    item['reviewer']=item['reviewer'].pop();
                    item['overall'] = site.select('.//*[contains(@class, "info")]/span[1]/span[1]/@class').extract()
                    if (len(item['overall']) != 0):
                        item['overall'] = re.search("(\d+)", str(item['overall'].pop())).group(1)
                    else:
                        item['overall'] = ''
                    item['comfort'] = site.select('.//*[contains(@class, "info")]/span[2]/span[1]/@class').extract()
                    if (len(item['comfort']) != 0):
                        item['comfort']=re.search("(\d+)", str(item['comfort'].pop())).group(1)
                    else:
                        item['comfort']= ''
                    item['size'] = site.select('.//*[contains(@class, "feel")]/span[1]/strong[.="Shoe Size:"]/following-sibling::text()[1]').extract()
                    if (len(item['size']) != 0):
                        item['size'] = item['size'].pop();
                    else:
                        item['size'] = ''
                    item['arch'] = site.select('.//*[contains(@class, "feel")]/span[2]/strong[.="Shoe Arch:"]/following-sibling::text()[1]').extract()
                    if (len(item['arch']) != 0):
                        item['arch'] = item['arch'].pop();
                    else:
                        item['arch'] = ''
                    item['width'] = site.select('.//*[contains(@class, "feel")]/span[3]/strong[.="Shoe Width:"]/following-sibling::text()[1]').extract()
                    if ( len(item['width']) != 0 ):
                        item['width'] = item['width'].pop();
                    else:
                        item['width']=''
                    '''summary = site.select('./*[contains(@class, "summary")]/p//text()').extract()
                    #summary = site.select('.//*[contains(@class, "summary")]/p').extract()
                    print("Initial Node val %s" % site.select('./*[contains(@class, "summary")]/p'))
                    print("Response %s" % response.url)
                    #for i,node in enumerate(site.select('.//*[contains(@class, "summary")]/p')):
                    #    print("Printing")
                    #    print(i, node)
                    description = ""
                    while (len(summary) != 0):
                        description = description + summary.pop(0).encode('utf-8')
                    description = str(description)
                    print("DESC :::::::::::::::: %s" %description)
                    sleep(3)'''
                    description=""
                    for p in site.select('.//*[contains(@class, "summary")]/p'):
                        summary = p.select('.//text()').extract()
                    while (len(summary) != 0):
                        description = description + summary.pop(0).encode('utf-8')
                    description = str(description)
                    item['Description'] = description
                    item['url'] = response.url
                    print("Finished parsing the product %s" % response.url)
                    yield item
