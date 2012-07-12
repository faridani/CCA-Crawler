---------README ----------------------
**************************************************************************************

From scratch
1) Follow the instructions mentioned in http://doc.scrapy.org/en/0.14/intro/install.html to install scrapy

For running scrapy on this machine.
2) The code structure/directory structure is automatically created in the designated directory once scrapy is installed.
3) We need to run the code file crawler_spider.py present within the spiders directory of the project.
4) open the command prompt and navigate to the scrapy folder
5) To get the data in csv format run the following command
scrapy crawl zappos.com --set FEED_URI=test104.csv --set FEED_FORMAT=csv