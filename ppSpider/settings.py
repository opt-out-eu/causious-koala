# -*- coding: utf-8 -*-

# Scrapy settings for emailSpider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import logging

BOT_NAME = 'ppSpider'
SPLASH = False
CRAELERA = False


SPIDER_MODULES = ['ppSpider.spiders']
NEWSPIDER_MODULE = 'ppSpider.spiders'

USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'companyEmail (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 10

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 1
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    'companyEmail.pipelines.CompanyemailPipeline': 300,
#}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []

LOG_LEVEL = logging.ERROR
LOG_FILE = 'scrapy.log'

#Export as CSV Feed
FEED_FORMAT = "csv"
FEED_EXPORT_FIELDS = ['domain', 'alexa_rank', 'pp_url', 'link_text']
FEED_URI = "pp-list.csv"


if SPLASH:
	DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'
	HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'

	#SPLASH_URL = 'https://ipbkb1bg-splash.scrapinghub.com/'
	SPLASH_URL = 'http://localhost:8050/'
	DOWNLOADER_MIDDLEWARES['scrapy_splash.SplashCookiesMiddleware'] = 723
	DOWNLOADER_MIDDLEWARES['scrapy_splash.SplashMiddleware'] = 725
	SPIDER_MIDDLEWARES = {
    	'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
	}

if CRAELERA:
	DOWNLOADER_MIDDLEWARES['scrapy_crawlera.CrawleraMiddleware'] = 610
	CRAWLERA_ENABLED = True
	CRAWLERA_APIKEY = 'a247c0035f6e489ca820c0f3d1fe9a37'
