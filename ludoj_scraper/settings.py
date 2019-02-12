# -*- coding: utf-8 -*-

''' Scrapy settings '''

import os

try:
    from dotenv import load_dotenv
    load_dotenv(verbose=True)
except ImportError:
    pass

BOT_NAME = 'ludoj'

SPIDER_MODULES = ['ludoj_scraper.spiders']
NEWSPIDER_MODULE = 'ludoj_scraper.spiders'

LOG_LEVEL = 'INFO'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FEED_EXPORT_FIELDS = (
    'name',
    'alt_name',
    'year',
    'game_type',
    'description',
    'designer',
    'artist',
    'publisher',
    'url',
    'official_url',
    'image_url',
    'image_file',
    'video_url',
    'rules_url',
    'rules_file',
    'review_url',
    'external_link',
    'list_price',
    'min_players',
    'max_players',
    'min_players_rec',
    'max_players_rec',
    'min_players_best',
    'max_players_best',
    'min_age',
    'max_age',
    'min_age_rec',
    'max_age_rec',
    'min_time',
    'max_time',
    'category',
    'mechanic',
    'cooperative',
    'compilation',
    'compilation_of',
    'family',
    'expansion',
    'implementation',
    'integration',
    'rank',
    'num_votes',
    'avg_rating',
    'stddev_rating',
    'bayes_rating',
    'worst_rating',
    'best_rating',
    'complexity',
    'easiest_complexity',
    'hardest_complexity',
    'language_dependency',
    'lowest_language_dependency',
    'highest_language_dependency',
    'bgg_id',
    'freebase_id',
    'wikidata_id',
    'wikipedia_id',
    'dbpedia_id',
    'luding_id',
    'spielen_id',
    'bga_id',
    'published_at',
    'updated_at',
    'scraped_at',
)

MULTI_FEED_ENABLED = True
MULTI_FEED_EXPORT_FIELDS = {
    'GameItem': FEED_EXPORT_FIELDS,
    'RatingItem': (
        'bgg_id',
        'bgg_user_name',
        'bgg_user_rating',
        'bgg_user_owned',
        'bgg_user_prev_owned',
        'bgg_user_for_trade',
        'bgg_user_want_in_trade',
        'bgg_user_want_to_play',
        'bgg_user_want_to_buy',
        'bgg_user_preordered',
        'bgg_user_wishlist',
        'bgg_user_play_count',
        'published_at',
        'updated_at',
        'scraped_at',
    )
}

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'ludoj (+http://www.yourdomain.com)'
# USER_AGENT = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) '
#               'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36')

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = .1
# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 8
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en',
}

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'ludoj_scraper.middlewares.MyCustomSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'ludoj_scraper.middlewares.DelayedRetry': 555,
}

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
EXTENSIONS = {
    'scrapy.extensions.feedexport.FeedExporter': None,
    'ludoj_scraper.extensions.MultiFeedExporter': 0,
    'scrapy.extensions.throttle.AutoThrottle': None,
    'ludoj_scraper.extensions.NicerAutoThrottle': 0,
    'ludoj_scraper.extensions.StateTag': 0,
    'ludoj_scraper.extensions.MonitorDownloadsExtension': 500,
    'ludoj_scraper.extensions.DumpStatsExtension': 500,
}

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'ludoj_scraper.pipelines.DataTypePipeline': 100,
    'ludoj_scraper.pipelines.ValidatePipeline': 200,
    'ludoj_scraper.pipelines.ResolveLabelPipeline': 300,
    'ludoj_scraper.pipelines.ResolveImagePipeline': 400,
    'scrapy.pipelines.images.ImagesPipeline': 500,
    'scrapy.pipelines.images.FilesPipeline': 600,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
# The initial download delay
AUTOTHROTTLE_START_DELAY = max(DOWNLOAD_DELAY * 2, 5)
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
AUTOTHROTTLE_TARGET_CONCURRENCY = CONCURRENT_REQUESTS_PER_DOMAIN
# Enable showing throttling stats for every response received:
AUTOTHROTTLE_DEBUG = False
AUTOTHROTTLE_HTTP_CODES = (429,)

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 60 * 60 * 24 * 7 # 1 week
#HTTPCACHE_DIR = 'httpcache'
HTTPCACHE_IGNORE_HTTP_CODES = (500, 502, 503, 504, 408, 429, 202)
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
HTTPCACHE_POLICY = 'scrapy.extensions.httpcache.RFC2616Policy'

RETRY_ENABLED = True
RETRY_HTTP_CODES = (500, 502, 503, 504, 408, 429)

DELAYED_RETRY_ENABLED = False
DELAYED_RETRY_TIMES = -1
DELAYED_RETRY_HTTP_CODES = ()
DELAYED_RETRY_DELAY = 10.0
DELAYED_RETRY_PRIORITY_ADJUST = 0
DELAYED_RETRY_BACKOFF = True
DELAYED_RETRY_BACKOFF_MAX_DELAY = 100.0

# Monitoring settings
MONITOR_DOWNLOADS_ENABLED = True
MONITOR_DOWNLOADS_INTERVAL = 60
DUMP_STATS_ENABLED = True
DUMP_STATS_INTERVAL = 5 * 60

# Spider settings
SCRAPE_BGG_RATINGS = True
SCRAPE_BGG_COLLECTIONS = True

# State tags
STATE_TAG_FILE = '.state'
PID_TAG_FILE = '.pid'

MEDIA_ALLOW_REDIRECTS = True

# Image processing
IMAGES_STORE = os.path.join(BASE_DIR, 'images')
IMAGES_URLS_FIELD = 'image_url'
IMAGES_RESULT_FIELD = 'image_file'
IMAGES_EXPIRES = 180
IMAGES_THUMBS = {
    'thumb': (1024, 1024),
}

# File processing
FILES_STORE = os.path.join(BASE_DIR, 'rules')
FILES_URLS_FIELD = 'rules_url'
FILES_RESULT_FIELD = 'rules_file'
FILES_EXPIRES = 180

# Board Game Atlas
BGA_CLIENT_ID = os.getenv('BGA_CLIENT_ID')
BGA_SCRAPE_IMAGES = False
BGA_SCRAPE_VIDEOS = False
BGA_SCRAPE_REVIEWS = False