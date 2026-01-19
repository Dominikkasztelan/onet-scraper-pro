
import pytest
from scrapy.http import HtmlResponse
from onet_scraper.spiders.onet import OnetSpider

def test_rules_match_article_urls():
    spider = OnetSpider()
    # Assume the generic article rule is index 1 (based on source code inspection)
    # Rule index 1: allow=.../[a-z0-9-]+/[a-z0-9-]+/[a-z0-9]+
    
    # We need to find the rule that calls 'parse_item'
    article_rule = None
    for rule in spider.rules:
        if rule.callback == 'parse_item':
            article_rule = rule
            break
            
    assert article_rule is not None, "Could not find rule with parse_item callback"
    
    # Valid matching URLs
    valid_urls = [
        "https://wiadomosci.onet.pl/kraj/tytul-artykulu/xyz123",
        "https://wiadomosci.onet.pl/swiat/inny-artykul/abc999"
    ]
    
    # Invalid URLs (should NOT match)
    invalid_urls = [
        "https://wiadomosci.onet.pl/tylko-kategoria/cos", # Too short depth
        "https://wiadomosci.onet.pl/kraj/tytul",         # Missing ID
        "https://wiadomosci.onet.pl/oferta/reklama/123"  # Contains 'oferta' which is denied in another param, but LinkExtractor logic is complex to test fully without link object. 
        # Ideally we test LinkExtractor.extract_links but that requires Response object.
    ]

    # Testing LinkExtractor allow pattern
    extractor = article_rule.link_extractor
    
    # To test regex matches, we can peek at allow_Res (compiled regexes)
    # or simulate extraction from a dummy page containing these links.
    
    link_html = ""
    for url in valid_urls + invalid_urls:
        link_html += f'<a href="{url}" class="ods-c-card-wrapper">Link</a>\n'
        
    response = HtmlResponse(
        url="https://wiadomosci.onet.pl/",
        body=f"<html><body>{link_html}</body></html>".encode('utf-8')
    )
    
    links = extractor.extract_links(response)
    extracted_urls = [link.url for link in links]
    
    for url in valid_urls:
        assert url in extracted_urls, f"Should extract {url}"
        
    for url in invalid_urls:
        assert url not in extracted_urls, f"Should NOT extract {url}"

def test_rules_deny_patterns():
    spider = OnetSpider()
    article_rule = next(r for r in spider.rules if r.callback == 'parse_item')
    extractor = article_rule.link_extractor
    
    denied_urls = [
        "https://wiadomosci.onet.pl/kraj/artykul-sponsorowany/123?utm=sponsored", # 'sponsored' in deny?
        "https://wiadomosci.onet.pl/partner/artykul/123"
    ]
    
    # We must ensure 'partner' or 'sponsored' is actually in the URL string to fail the regex check if deny is used.
    # The LinkExtractor deny works on the URL.
    
    link_html = ""
    for url in denied_urls:
        link_html += f'<a href="{url}" class="ods-c-card-wrapper">Link</a>\n'
        
    response = HtmlResponse(
        url="https://wiadomosci.onet.pl/",
        body=f"<html><body>{link_html}</body></html>".encode('utf-8')
    )
    
    links = extractor.extract_links(response)
    extracted_urls = [link.url for link in links]
    
    # Checking specific deny rules from onet.py:
    # deny=(r'#', r'autorzy', r'oferta', r'partner', r'reklama', r'promocje', r'sponsored')
    
    for url in denied_urls:
         # Assert that NONE of the denied URLs were extracted
         assert url not in extracted_urls, f"Should NOT extract denied URL: {url}"
