from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.http import Request
import string
import re

from zappos.items import ZapposItem

class women_shoes_spider (CrawlSpider):
    name = "zappos"
    allowed_domains = ['zappos.com']
    start_urls = ['http://www.zappos.com/womens-shoes~1i7']
    ##Stack (or queue) for keeping track of crawled sites
    ##crawled = []
    ##Only follow URLs containing the word "womens" followed by anything (because
    ##this includes all types of women's shoes)
    rules = (
             Rule(SgmlLinkExtractor(allow=(r'/womens\-.'), restrict_xpaths=('//div[@id="FCTzc2Select"]')), callback='parse_category'),
             )

    ##Traverse all shoes in selected category;
    ##This is called recursively to go from the 1st page to 2nd, 2nd to 3rd, etc.
    def parse_category (self, response):
        hxs = HtmlXPathSelector(response)

        page_div = hxs.select('//div[@class="sort top"]//div[@class="pagination"]')
        ##current page of shoes##
        current_page_temp = page_div.select('./text()').extract()
        ##We must check if current_page is a null list to avoid index out-of-bounds error.
        current_page = ""
        if current_page_temp:
            current_page = filter(lambda x: not x == ' ', current_page_temp)[0]
        else:
            current_page = -1

        ##If meta length is 5, this means this is the first call to parse_category,
        ##in which case we just manually select and extract the last page number.
        ##Otherwise, we use the passed in meta value.
        if len(response.meta) == 5:
            last_page = page_div.select('.//span[@class="last"]//a/text()')
            ##At least one shoe category page is formatted so that there is no span whose class is "last".
            ##We must check for this.
            if not last_page:
                i = len(page_div.select('.//a')) - 1
                last_page = page_div.select('.//a[%d]/text()' % i)
            if last_page:
                last_page = last_page.extract()[0]
            else:
                last_page = -1
        else:
            last_page = response.meta['last_page']

        ##Iterate through each shoe on the page##
        shoes = hxs.select('//div[@id="searchResults"]//a')
        for shoe in shoes:
            shoe_url = "http://" + self.allowed_domains[0] + shoe.select('@href').extract()[0]
            shoe_name = shoe.select('.//span[@class="productName"]/text()').extract()[0]
            request = Request(shoe_url, callback = self.parse_shoe)
            request.meta['name'] = shoe_name
            yield request

        ##If current_page is last page, do not recurse, because there
        ##are no pages left to traverse.
        if not int(current_page) == int(last_page):
            next_page_selector = page_div.select('.//a[contains(@class, "btn secondary arrow pager")]')
            ##The next_page button is always the last "secondary arrow pager" in the list of selectors.
            index = len(next_page_selector)
            next_page = next_page_selector[index - 1].select('@href').extract()[0]
            request = Request("http://" + self.allowed_domains[0] + next_page, callback = self.parse_category)
            request.meta['last_page'] = last_page
            yield request
        else:
            yield None

    def parse_shoe (self, response):
        hxs = HtmlXPathSelector(response)

        ##String manipulation to create true url (easier to navigate, select, and extract)

        ##shoe id##
        shoe_sku_id = hxs.select('//span[contains(@class, "sku")]/text()').extract()[0]
        shoe_id = shoe_sku_id.split()[1]
        ###########
        true_url = ("http://" + self.allowed_domains[0] + '/' + "product" + '/' + "review" +
                    '/' + shoe_id + '/' + "page" + '/' + '1')
        request = Request(true_url, callback = self.parse_reviews_lvl1)
        request.meta['name'] = response.meta['name']
        request.meta['id'] = shoe_id
        yield request

    ##Loops through the pages of reviews for one product;
    ##does not loop through the reviews on each page.
    ##In other words, this loop traverses the pages, calling
    ##the next level parse method to parse the reviews.
    def parse_reviews_lvl1 (self, response):
        hxs = HtmlXPathSelector(response)
        ##some product info##
        product_name = response.meta['name']
        product_id = response.meta['id']
        
        ##number of pages of reviews##
        num_pages_selector = hxs.select('//p[@class="top-pagination"]//a')
        
        ##If selector list is empty, this can mean either:
        ##  *that there is only 1 page of reviews
        ##  *that there are no reviews
        ##In both cases, we will set num_pages = 2.
        num_pages = 2
        
        ##Otherwise, extract number of pages from html.
        if num_pages_selector:
            num_pages = num_pages_selector[len(num_pages_selector) - 2].select('text()').extract()[0]

        ##Loop through all pages.
        num_pages_int = int(num_pages)
        for page_num in range(1, num_pages_int + 1):
            non_numbered_url = response.url[0 : response.url.find("page/") + 5]
            numbered_url = non_numbered_url + str(page_num)
            request = Request(numbered_url, callback = self.parse_reviews_lvl2)
            request.meta['name'] = product_name
            request.meta['id'] = product_id
            request.meta['url'] = numbered_url
            yield request

    ##Parse reviews.
    def parse_reviews_lvl2 (self, response):
        ##If url_toAdd is in the crawled list of URLs, then simply return.
        ##Otherwise, append it to crawled, and continue with parsing.
        ##url_toAdd = response.url
        ##if url_toAdd in self.crawled:
            ##return
        ##self.crawled.append(url_toAdd)

        hxs = HtmlXPathSelector(response)
        product_name = response.meta['name']
        product_id = response.meta['id']
        url = response.meta['url']
        reviews = hxs.select('//div[@class="review first" or @class="review"]')
        ##If reviews is empty, that means there are no reviews on this page, so we return from the function.
        if not reviews:
            return
        for review in reviews:
            content = review.select('.//div[@class="reviewContent"]//div[@class="reviewText gray"]')
            
            ##some basic product info
            date = review.select('.//div[@class="reviewContent"]//div[@class="reviewDate"]//p/text()').extract()[0]
            reviewer = content.select('.//h3/text()').extract()[0].strip()
            location = content.select('.//p[@class="reviewerLocation"]/text()').extract()[0].strip()
            
            ##process descriptions
            description_list =  content.select('.//p[@class="reviewSummary"]//text()').extract()
            for segment in description_list:
                current_index = description_list.index(segment)
                ##previous_index = current_index - 1
                ##rest = segment[1:]
                ##first = segment[0]
                ##if re.match('[.,!?]', first):
                    ##description_list[current_index] = rest
                    ##description_list[previous_index] = description_list[previous_index] + first
                description_list[current_index] = string.replace(segment, '\n', '')
                description_list[current_index] = string.replace(segment, '\r', '')
                description_list[current_index] = string.replace(segment, '\r\n', '')
                            
            description = "".join(description_list)

            ##star ratings (overall, comfort, style)
            product_ratings = content.select('.//div[@class="productRatings"]//p')
            ##overall
            overall_rat = product_ratings[0].select('.//span[contains(@class, "stars rating")]/text()').extract()[0]
            overall = re.findall(r'\d+', overall_rat)[0]
            ##comfort
            comfort_rat = product_ratings[1].select('.//span[contains(@class, "stars rating")]/text()').extract()[0]
            comfort = re.findall(r'\d+', comfort_rat)[0]
            ##style
            style_rat = product_ratings[2].select('.//span[contains(@class, "stars rating")]/text()').extract()[0]
            style = re.findall(r'\d+', style_rat)[0]

            ##slider fit ratings
            fit_ratings = review.select('.//div[@class="productFeel"]')
            ##some reviews do not have fit ratings
            size, arch, width = None, None, None
            if fit_ratings:
                ##Any one of these ratings can be absent. We must account for this.
                ##If the rating is not empty, we extract the rating. Otherwise, we leave it as None.
                sizeTemp = fit_ratings.select('.//div[@class="productShoeSize clearfix"]//p[contains(@class, "feelIndicator feelLevel")]/text()').extract()
                archTemp = fit_ratings.select('.//div[@class="productShoeArch clearfix"]//p[contains(@class, "feelIndicator feelLevel")]/text()').extract()
                widthTemp = fit_ratings.select('.//div[@class="productShoeWidth clearfix"]//p[contains(@class, "feelIndicator feelLevel")]/text()').extract()
                if sizeTemp:
                    size = sizeTemp[0]
                if archTemp:
                    arch = archTemp[0]
                if widthTemp:
                    width = widthTemp[0]

            ##Instantiation and specification of the review item to be yielded.
            item = ZapposItem()
            item['product_name'] = product_name
            item['product_id'] = product_id
            item['posted'] = date
            item['reviewer'] = reviewer
            item['location'] = location
            item['overall'] = overall
            item['comfort'] = comfort
            item['style'] = style
            item['size'] = size
            item['arch'] = arch
            item['width'] = width
            item['description'] = description
            item['url'] = url
            
            yield item



