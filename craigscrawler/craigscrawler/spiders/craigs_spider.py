from scrapy.spider import CrawlSpider
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from craigscrawler.items import CraigscrawlerItem

class CraigsSpider(CrawlSpider):
    name = "craigslist"
    allowed_domains = ["craigslist.org"]
    search_terms = ["cyclocross", "cx"]
    query_base_url = "https://newyork.craigslist.org/search/bia?query="
    start_urls = [query_base_url + query for query in search_terms]
    rules = (
        Rule (
            LinkExtractor(restrict_xpaths=('//a[@class="button next"]',)),
            follow= True
        ),
        Rule (
            LinkExtractor(restrict_xpaths=('//p[@class="row"]/a[@class="i"]',)),
            callback='parse_item'
        )
    )

    def parse_item(self, response):
	hxs = Selector(response)
	title = hxs.xpath("//span[@id='titletextonly']/text()").extract()
        price = hxs.xpath("//span[@class='price']/text()").extract()
        description = hxs.xpath("//section[@id='postingbody']/text()").extract()
        main_image = hxs.xpath("//div[contains(@class,'visible')]//img/@src").extract()
        link = response.url
        self.log('%s' % hxs.xpath("//div[contains(@class,'visible')]//img/@src"))
        return CraigscrawlerItem(
            title=title,
            price=price,
            description=description,
            main_image=main_image,
            link=link
        )

    #def filter_by(self, node):
    #    return True


    #def parse(self, response):
    #    self.parse_search_results(response)

    #def parse_search_results(self, response):
    #    hxs = HtmlXPathSelector(response)
    #    rows = hxs.select("//p[@class='row']")
    #    filtered_rows = [row for row in rows if self.filter_by(row)]
    #    item_pages_urls = [
    #        filtered_row.select('.//a/@href').extract()
    #        for filtered_row in filtered_rows
    #    ]
    #    self.log('urls: %s' %item_pages_urls)
