import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from datetime import datetime
# Importujemy nasz model z pliku items.py
from onet_scraper.items import ArticleItem

class OnetSpider(CrawlSpider):
    """
    Spider for scraping Onet.pl news articles.
    
    RUNNING THE SPIDER:
    -------------------
    To run this spider, use the following command in your terminal:
    $ python -m scrapy crawl onet
    
    To run in debug mode (verbose logs):
    $ python debug_runner.py
    """
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
        
        # Strategy 1: JSON-LD
        json_ld_date = None
        ld_json_scripts = response.xpath('//script[@type="application/ld+json"]/text()').getall()
        # Init variables for new fields
        author = None
        section = None
        date_modified = None
        image_url = None
        
        import json
        for script in ld_json_scripts:
            try:
                data = json.loads(script)
                
                # Helper to process a JSON-LD node
                def process_node(node):
                    nonlocal json_ld_date, author, section, date_modified, image_url
                    if 'datePublished' in node:
                        json_ld_date = node['datePublished']
                    if 'dateModified' in node:
                        date_modified = node['dateModified']
                    if 'author' in node:
                        if isinstance(node['author'], dict) and 'name' in node['author']:
                            author = node['author']['name']
                        elif isinstance(node['author'], list) and len(node['author']) > 0 and 'name' in node['author'][0]:
                            author = node['author'][0]['name']
                    if 'articleSection' in node:
                        section = node['articleSection']
                    if 'image' in node:
                        if isinstance(node['image'], dict) and 'url' in node['image']:
                            image_url = node['image']['url']
                        elif isinstance(node['image'], str):
                            image_url = node['image']

                # Handle @graph structure
                if '@graph' in data:
                    for node in data['@graph']:
                        process_node(node)
                # Handle direct structure
                else:
                    process_node(data)
                
                if json_ld_date:
                    break
            except:
                continue

        # Fallback for Author if JSON-LD failed
        if not author:
             # Based on user feedback/image
             author = response.css('.ods-m-author-xl__name-link::text').get()
             if not author:
                 author = response.css('.ods-m-author-xl__name::text').get() # Without link
             if not author:
                 author = response.css('.authorName::text').get() # Old potential class
             
             if author:
                 author = author.strip()


        # Strategy 2: Visible date (updated class)
        visible_date = response.css('.ods-m-date-authorship__publication::text').get()
        if not visible_date:
            # Try a broader selector just in case
            visible_date = response.xpath('//span[contains(@class, "date")]/text()').get()
        
        
        date_to_check = json_ld_date if json_ld_date else visible_date

        if date_to_check:
            article_date_str = date_to_check[:10].strip()
            try:
                article_date = datetime.strptime(article_date_str, '%Y-%m-%d')
                today = datetime.now()
                days_diff = (today - article_date).days
                
                # FILTER: Allow articles from the last 3 days
                if 0 <= days_diff <= 3:
                    try:
                        # Extract content
                        content_list = response.css('.hyphenate::text').getall()
                        if not content_list:
                            # Fallback to all P tags if .hyphenate missing, filtering short/empty
                            ps = response.css('p::text').getall()
                            content_list = [t for t in ps if len(t.strip()) > 30]
                        
                        full_content = "\n".join([c.strip() for c in content_list if c.strip()])
                        
                        # --- Extra Fields Logic ---
                        # Keywords
                        keywords = response.xpath('//meta[@name="keywords"]/@content').get()
                        
                        # ID (Internal)
                        # Try data-story-id
                        internal_id = response.xpath('//meta[@name="data-story-id"]/@content').get()
                        if not internal_id:
                            # Fallback: extract from URL
                            import re
                            id_match = re.search(r'/([a-z0-9]+)$', response.url)
                            if id_match:
                                internal_id = id_match.group(1)
                                
                        # Read Time (Estimate if not present)
                        # 200 words per minute
                        word_count = len(full_content.split())
                        read_time = max(1, round(word_count / 200))

                        if not image_url:
                            image_url = response.xpath('//meta[@property="og:image"]/@content').get()

                        # --- Content Cleaning ---
                        # Normalize text to handle &nbsp; (\xa0) and other weird whitespace
                        clean_content = full_content.replace('\xa0', ' ')
                        
                        # Filter out known boilerplates
                        scam_phrases = [
                            "Dołącz do Premium",
                            "i odblokuj wszystkie funkcje", 
                            "dla materiałów Premium",
                            "Onet Premium",
                            "Kliknij tutaj",
                            "Zobacz także",
                            "redakcja", # Often at the end
                            "Źródło:"
                        ]
                        
                        # Cutoff markers - stop reading if we hit these
                        cutoff_markers = [
                            "Dołącz do Premium",
                            "i odblokuj wszystkie funkcje",
                            "Zobacz także",
                            "Onet Premium"
                        ]
                        
                        for marker in cutoff_markers:
                            if marker in clean_content:
                                clean_content = clean_content.split(marker)[0]
                        
                        # Remove other junk lines
                        lines = clean_content.split('\n')
                        filtered_lines = []
                        for line in lines:
                            # Skip lines containing scam phrases (double check after split)
                            if any(phrase in line for phrase in scam_phrases):
                                continue
                            # Skip lines that are just whitespace
                            if not line.strip():
                                continue
                            # Skip very short lines that might be artifacts (unless they look like subheaders?)
                            # Relaxed length check to 3 to allow valid short words/numbers, but keep it tight
                            if len(line.strip()) < 3: 
                                continue
                            filtered_lines.append(line)
                        
                        clean_content = "\n".join(filtered_lines).strip()

                        # Tworzymy i walidujemy item
                        item = ArticleItem(
                            title=response.css('h1::text').get(),
                            url=response.url,
                            date=article_date_str,
                            lead=response.css('#lead::text').get(),
                            content=clean_content, # Use cleaned content
                            author=author,
                            keywords=keywords,
                            section=section,
                            date_modified=date_modified,
                            image_url=image_url,
                            id=internal_id,
                            read_time=read_time
                        )
                        self.logger.info(f"✅ ZAPISANO: {article_date_str} | {response.url}")
                        yield item.model_dump()
                    except Exception as e:
                        self.logger.error(f"❌ BŁĄD DANYCH: {e}")
                else:
                    self.logger.info(f"⚠️ POMINIĘTO (DATA): {article_date_str} | {response.url}")
            except ValueError:
                 self.logger.error(f"❌ BŁĄD DATY: {article_date_str} | {response.url}")