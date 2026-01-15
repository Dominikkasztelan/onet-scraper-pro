
import sys
import os
import pytest
from scrapy.http import HtmlResponse, Request
from onet_scraper.spiders.onet import OnetSpider

# Mock HTML content
MOCK_HTML_WITH_JSON_LD = """
<html>
    <head>
        <script type="application/ld+json">
        {
            "@graph": [
                {
                    "@context": "https://schema.org",
                    "@type": "NewsArticle",
                    "datePublished": "2026-01-15T12:00:00+01:00",
                    "dateModified": "2026-01-15T13:00:00+01:00",
                    "author": {
                        "@type": "Person",
                        "name": "Test Author"
                    },
                    "headline": "Test Title",
                    "articleSection": "Test Section",
                    "image": {
                        "url": "http://example.com/image.jpg"
                    }
                }
            ]
        }
        </script>
        <meta name="keywords" content="test, news, scraper">
        <meta name="data-story-id" content="test1234">
    </head>
    <body class="hyphenate">
        <h1>Test Title</h1>
        <div id="lead">Test Lead</div>
        <p>This is the first paragraph of content which is definitely longer than thirty characters to pass the filter.</p>
        <p>This is the second paragraph which contains the phrase Dołącz do Premium text and should be cut off.</p>
        <p class="ods-m-author-xl__name-link">Fallback Author</p>
    </body>
</html>
"""

@pytest.fixture
def spider():
    return OnetSpider()

def test_parse_item_json_ld(spider):
    request = Request(url="https://wiadomosci.onet.pl/test-article")
    response = HtmlResponse(
        url="https://wiadomosci.onet.pl/test-article",
        request=request,
        body=MOCK_HTML_WITH_JSON_LD.encode('utf-8')
    )
    
    # Run the generator and get the first result
    results = list(spider.parse_item(response))
    assert len(results) == 1
    item = results[0]
    
    assert item['title'] == "Test Title"
    assert item['author'] == "Test Author"
    assert item['section'] == "Test Section"
    assert "This is the first paragraph" in item['content']
    assert "Dołącz do Premium" not in item['content'] # Should be cleaned
    assert item['id'] == "test1234"
    assert item['keywords'] == "test, news, scraper"

def test_parse_item_fallback(spider):
    # HTML WITHOUT JSON-LD
    html = """
    <html>
        <body>
            <h1>Fallback Title</h1>
            <div id="lead">Fallback Lead</div>
            <span class="ods-m-date-authorship__publication">2026-01-14 10:00</span>
            <span class="ods-m-author-xl__name-link">Fallback Author</span>
            <p class="hyphenate">Some content here.</p>
        </body>
    </html>
    """
    request = Request(url="https://wiadomosci.onet.pl/fallback-article")
    response = HtmlResponse(
        url="https://wiadomosci.onet.pl/fallback-article",
        request=request,
        body=html.encode('utf-8')
    )
    
    results = list(spider.parse_item(response))
    assert len(results) == 1
    item = results[0]
    
    assert item['title'] == "Fallback Title"
    assert item['author'] == "Fallback Author"
    assert item['date'] == "2026-01-14"

def test_parse_item_filters_old_articles(spider):
    # Article from 2020 (way older than 3 days)
    html = """
    <html>
        <head>
            <script type="application/ld+json">
            {
                "@context": "https://schema.org",
                "@type": "NewsArticle",
                "datePublished": "2020-01-01T12:00:00+01:00", 
                "headline": "Old News"
            }
            </script>
        </head>
        <body class="hyphenate">
            <h1>Old Title</h1>
        </body>
    </html>
    """
    request = Request(url="https://wiadomosci.onet.pl/old-article")
    response = HtmlResponse(
        url="https://wiadomosci.onet.pl/old-article",
        request=request,
        body=html.encode('utf-8')
    )
    
    # Should yield nothing because it's filtered
    results = list(spider.parse_item(response))
    assert len(results) == 0

def test_parse_item_malformed_json_ld(spider):
    # JSON-LD is broken/invalid JSON
    html = """
    <html>
        <head>
            <script type="application/ld+json">
            { broken json here ... 
            </script>
        </head>
        <body>
            <h1>Title</h1>
            <div id="lead">Lead</div>
            <span class="ods-m-date-authorship__publication">2026-01-15 10:00</span>
            <p class="hyphenate">Content must be present.</p>
        </body>
    </html>
    """
    request = Request(url="https://wiadomosci.onet.pl/malformed")
    response = HtmlResponse(
        url="https://wiadomosci.onet.pl/malformed",
        request=request,
        body=html.encode('utf-8')
    )
    
    # Should handle error gracefully and try fallback/cleanup logic
    # In this mock, we have valid fallback date in span, so it SHOULD succeed
    results = list(spider.parse_item(response))
    assert len(results) == 1
    assert results[0]['title'] == "Title"
