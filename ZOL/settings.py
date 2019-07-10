# -*- coding: utf-8 -*-

# Scrapy settings for ZOL project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'ZOL'

SPIDER_MODULES = ['ZOL.spiders']
NEWSPIDER_MODULE = 'ZOL.spiders'

#for cloud
# MONGO_HOST = '118.25.188.238'
# MONGO_PORT = 27017
# MONGO_DB = 'phoneYelp'
# MONGO_COLL = 'phoneList'
# MONGO_USER = 'phoneYelp_rw'
# MONGO_PSW = '123456'

#for local
MONGO_HOST = '127.0.0.1'
MONGO_PORT = 27017
MONGO_DB = 'phoneYelp'
MONGO_COLL = 'phoneList'
MONGO_USER = 'phoneYelp_rw'
MONGO_PSW = '123456'

#splash服务器地址
SPLASH_URL = 'http://127.0.0.1:8050'

#FEED_EXPORT_FIELDS = ["phoneID", "phoneName", "phoneParam", "phonePic"]
# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'ZOL (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 200

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 0.2
# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 200
CONCURRENT_REQUESTS_PER_IP = 200

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
SPIDER_MIDDLEWARES = {
    'ZOL.middlewares.ZolSpiderMiddleware': 543,
    'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
}

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'ZOL.middlewares.ZolDownloaderMiddleware': 300,
    'scrapy_splash.SplashCookiesMiddleware': 723,
    'scrapy_splash.SplashMiddleware': 725,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
}

# 去重过滤器
DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'
# 使用Splash的Http缓存
HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'ZOL.pipelines.ZolPipeline': 100,
    #'ZOL.pipelines.MongoPipeline': 200,
    'ZOL.pipelines.ImgDownLoadPipeline': 300,
    #'scrapy.pipeline.images.ImagesPipeline': 1
}
#设置图片存储目录
IMAGES_STORE = r'D:\Scrapy\ZOL_imgs'

# 避免下载最近30天已经下载过的图像内容
IMAGES_EXPIRES = 30

# 设置图片缩略图
IMAGES_THUMBS = {
    'small': (50, 50),
    'big': (250, 250),
}

# 图片过滤器，最小高度和宽度，低于此尺寸不下载
IMAGES_MIN_HEIGHT = 110
IMAGES_MIN_WIDTH = 110

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
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
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
