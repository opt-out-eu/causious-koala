import pkgutil

import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy_splash import SplashRequest
from scrapy.http import Request
from w3lib.url import safe_url_string
from ppSpider import settings


URL_RESOURCE_NAME = 'data/majestic-top-10k.csv'
HTTP_PREFIX = 'http://'
LUA_SOURCE = pkgutil.get_data('ppSpider', 'scripts/crawlera.lua').decode('utf-8')


def make_request(url, callback, errback):
	if settings.SPLASH:
		return SplashRequest(
			url, 
			callback,
			endpoint='render.html',
			args={
				'viewport':'full',
				'render_all': 1,
				'lua_source': LUA_SOURCE,
				'crawlera_user': settings.CRAWLERA_APIKEY,
				'wait': .5,
				},
			cache_args=['lua_source']
			)
	else:
		return Request(
			url=url, 
			callback=callback,
			errback=errback
			)


class PrivacyPolicyItem(scrapy.Item):
	domain = scrapy.Field() 
	alexa_rank = scrapy.Field()
	pp_url = scrapy.Field()
	link_text = scrapy.Field()


class ppSpider(CrawlSpider):
	name = 'pp_spider'
	http_user = 'e56a3bc2612e408b803a9c9df6fd0d24'

	domainfile = pkgutil.get_data('ppSpider', URL_RESOURCE_NAME)
	domains = {domain.decode('utf-8').strip().split(",")[1]: domain.decode('utf-8').strip().split(",")[0] for domain in domainfile.splitlines()}
	start_urls = ['{0}{1}'.format(HTTP_PREFIX, domain) for domain in domains.keys()]

	def start_requests(self):
		for url in self.start_urls:
			request = make_request(url, self.parse, self.handleErrors)
			request.meta['domain'] =  url[len(HTTP_PREFIX):]
			self.logger.info('Start Requests %s' % request.url)
			yield request

	def parse(self, response):
		pp_re = '[Pp]rivacy'
		le = LinkExtractor(allow=(pp_re), unique=True)
		let = LinkExtractor(restrict_text=(pp_re), unique=True)
		links = le.extract_links(response) + let.extract_links(response)
		ppItems = set()
		for link in links:
			self.logger.info('--> pp page: {0}'.format(safe_url_string(link.url)))
			ppItem = PrivacyPolicyItem()
			ppItem["domain"] = response.meta['domain']
			ppItem["alexa_rank"] = self.domains[response.meta['domain']]
			ppItem["pp_url"] = link.url
			ppItem["link_text"] = link.text.strip()
			ppItems.add(ppItem)
		return ppItems

	def handleErrors(self, failure):
		self.logger.error(repr(failure))

		if failure.check(DNSLookupError):
            # this is the original request
            url = '{0}www.{1}'.format(HTTP_PREFIX, failure.request.url[len(HTTP_PREFIX):])
            request = make_request(url, self.parse, self.handleErrors)
            yield request
