import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from datetime import datetime
# Importujemy nasz model z pliku items.py
from onet_scraper.items import ArticleItem

class OnetSpider(CrawlSpider):
    name = 'onet'
    allowed_domains = ['wiadomosci.onet.pl']
    start_urls = ['https://wiadomosci.onet.pl/', 'https://wiadomosci.onet.pl/kraj', 'https://wiadomosci.onet.pl/swiat']

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'DOWNLOAD_DELAY': 1.0,
        'CONCURRENT_REQUESTS': 4,
        'DEPTH_LIMIT': 3,
        'CLOSESPIDER_PAGECOUNT': 200,
        'ROBOTSTXT_OBEY': False,
        'LOG_LEVEL': 'INFO'
    }

    rules = (
        Rule(LinkExtractor(allow=(r'archiwum', r'20\d\d-', r'pogoda', r'sport'), deny_domains=['przegladsportowy.onet.pl']), process_request='skip_request'),
        Rule(LinkExtractor(
            allow=(r'wiadomosci\.onet\.pl/[a-z0-9-]+/[a-z0-9-]+/[a-z0-9]+'), 
            deny=(r'#', r'autorzy', r'oferta', r'partner', r'reklama', r'promocje', r'sponsored'), 
            restrict_css=('.ods-c-card-wrapper', '.ods-o-card'),
            unique=True
        ), callback='parse_item', follow=False),
        Rule(LinkExtractor(allow=(r'wiadomosci.onet.pl'), restrict_xpaths='//a[contains(@class, "next")]'), follow=True),
    )

    def skip_request(self, request, response):
        return None

    def parse_item(self, response):
        json_ld_date = response.xpath('//meta[@property="article:published_time"]/@content').get()
        visible_date = response.css('.dateMeta::text').get()
        date_to_check = json_ld_date if json_ld_date else visible_date

        if date_to_check:
            article_date = date_to_check[:10].strip()
            today = datetime.now().strftime('%Y-%m-%d')

            if article_date == today:
                try:
                    # Tworzymy i walidujemy item
                    item = ArticleItem(
                        title=response.css('h1::text').get(),
                        url=response.url,
                        date=article_date,
                        lead=response.css('#lead::text').get()
                    )
                    self.logger.info(f"✅ ZAPISANO: {article_date} | {response.url}")
                    yield item.model_dump()
                except Exception as e:
                    self.logger.error(f"❌ BŁĄD DANYCH: {e}")