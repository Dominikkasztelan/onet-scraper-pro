# Scrapy settings for onet_scraper project
import os
from dotenv import load_dotenv

load_dotenv()

BOT_NAME = "onet_scraper"

SPIDER_MODULES = ["onet_scraper.spiders"]
NEWSPIDER_MODULE = "onet_scraper.spiders"

ADDONS = {}

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# Using a standard browser UA to blend in (Works on Windows/Linux)
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Concurrency and throttling settings
CONCURRENT_REQUESTS_PER_DOMAIN = 1
DOWNLOAD_DELAY = 2  # Slower but safer for 24/7 server operation

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Logging Configuration (Cross-platform compatible)
# Log to a file named 'scraper.log' in the project root
LOG_FILE = os.path.join(os.getcwd(), "scraper.log")
LOG_LEVEL = "INFO"

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    "onet_scraper.middlewares.TorMiddleware": 543,
}

# Tor Settings
TOR_PROXY = "socks5://127.0.0.1:9050"
TOR_CONTROL_PORT = 9051
TOR_PASSWORD = os.getenv("TOR_PASSWORD")
TOR_CONNECTION_TIMEOUT = 30  # Timeout for Tor requests in seconds
TOR_MAX_RETRIES = 3

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    "onet_scraper.pipelines.JsonWriterPipeline": 300,
}

# Set settings whose default value is deprecated to a future-proof value
FEED_EXPORT_ENCODING = "utf-8"

# Usage of asyncio reactor for async middleware support
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
