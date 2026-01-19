
import pytest
from datetime import datetime
from scrapy.http import HtmlResponse, Request
from onet_scraper.spiders.onet import OnetSpider

@pytest.fixture
def spider():
    return OnetSpider()

def create_mock_response(url, title, date, content, json_ld_valid=True):
    date = date or datetime.now().strftime('%Y-%m-%d')
    
    if json_ld_valid:
        json_section = f"""
            <script type="application/ld+json">
            {{
                "@graph": [
                    {{
                        "@context": "https://schema.org",
                        "@type": "NewsArticle",
                        "datePublished": "{date}T12:00:00+01:00",
                        "dateModified": "{date}T13:00:00+01:00",
                        "author": {{ "@type": "Person", "name": "Test Author" }},
                        "headline": "{title}",
                        "articleSection": "Test Section",
                        "image": {{ "url": "http://example.com/image.jpg" }}
                    }}
                ]
            }}
            </script>
        """
    else:
        # Invalid or missing JSON-LD
        if json_ld_valid is False:
             # Just invalid json
             json_section = '<script type="application/ld+json">{ broken json ... </script>'
        else:
             json_section = ""

    html = f"""
    <html>
        <head>
            {json_section}
            <meta name="keywords" content="test, news, scraper">
            <meta name="data-story-id" content="test1234">
        </head>
        <body class="hyphenate">
            <h1>{title}</h1>
            <div id="lead">Test Lead</div>
            <span class="ods-m-date-authorship__publication">{date} 10:00</span>
            <span class="ods-m-author-xl__name-link">Fallback Author</span>
            {content}
        </body>
    </html>
    """
    request = Request(url=url)
    return HtmlResponse(url=url, request=request, body=html.encode('utf-8'))


def test_parse_item_json_ld(spider):
    content = """
    <p>This is the first paragraph of content which is definitely longer than thirty characters to pass the filter.</p>
    <p>This is the second paragraph which contains the phrase Dołącz do Premium text and should be cut off.</p>
    """
    response = create_mock_response(
        url="https://wiadomosci.onet.pl/test-article",
        title="Test Title",
        date=None, # use today
        content=content,
        json_ld_valid=True
    )
    
    results = list(spider.parse_item(response))
    assert len(results) == 1
    item = results[0]
    
    assert item['title'] == "Test Title"
    assert item['author'] == "Test Author"
    assert item['section'] == "Test Section"
    assert "This is the first paragraph" in item['content']
    assert "Dołącz do Premium" not in item['content']
    assert item['id'] == "test1234"
    assert item['keywords'] == "test, news, scraper"

def test_parse_item_fallback(spider):
    content = '<p class="hyphenate">Some content here.</p>'
    response = create_mock_response(
        url="https://wiadomosci.onet.pl/fallback-article",
        title="Fallback Title",
        date=None,
        content=content,
        json_ld_valid=None # No JSON LD
    )
    
    results = list(spider.parse_item(response))
    assert len(results) == 1
    item = results[0]
    
    assert item['title'] == "Fallback Title"
    assert item['author'] == "Fallback Author"
    # Helper defaults date to today if None is passed
    assert item['date'] == datetime.now().strftime('%Y-%m-%d')

def test_parse_item_filters_old_articles(spider):
    response = create_mock_response(
        url="https://wiadomosci.onet.pl/old-article",
        title="Old Title",
        date="2020-01-01",
        content="<p>Old content</p>"
    )
    
    results = list(spider.parse_item(response))
    assert len(results) == 0

def test_parse_item_malformed_json_ld(spider):
    content = '<p class="hyphenate">Content must be present.</p>'
    response = create_mock_response(
        url="https://wiadomosci.onet.pl/malformed",
        title="Title",
        date=None,
        content=content,
        json_ld_valid=False # Broken JSON
    )
    
    results = list(spider.parse_item(response))
    assert len(results) == 1
    assert results[0]['title'] == "Title"

def test_parse_item_no_json_ld_uses_fallbacks(spider):
    """Test that spider correctly uses CSS fallbacks when JSON-LD is missing."""
    today_date = datetime.now().strftime('%Y-%m-%d')
    # HTML with no JSON-LD at all
    html = f"""
    <html>
        <head>
            <meta name="keywords" content="fallback, test">
            <meta name="data-story-id" content="fb123">
        </head>
        <body class="hyphenate">
            <h1>Fallback Title Test</h1>
            <div id="lead">Fallback Lead</div>
            <span class="ods-m-date-authorship__publication">{today_date} 14:30</span>
            <span class="ods-m-author-xl__name-link">Fallback Author Name</span>
            <p class="hyphenate">This is fallback content with more than thirty characters.</p>
        </body>
    </html>
    """
    request = Request(url="https://wiadomosci.onet.pl/fallback-test")
    response = HtmlResponse(url="https://wiadomosci.onet.pl/fallback-test", request=request, body=html.encode('utf-8'))
    
    results = list(spider.parse_item(response))
    assert len(results) == 1
    item = results[0]
    
    assert item['title'] == "Fallback Title Test"
    assert item['author'] == "Fallback Author Name"
    assert item['date'] == today_date
    assert item['id'] == "fb123"
    assert "fallback content" in item['content'].lower()

def test_parse_item_id_from_url(spider):
    """Test that ID is extracted from URL when meta tag is missing."""
    today_date = datetime.now().strftime('%Y-%m-%d')
    html = f"""
    <html>
        <head>
            <script type="application/ld+json">
            {{
                "@context": "https://schema.org",
                "@type": "NewsArticle",
                "datePublished": "{today_date}T12:00:00+01:00",
                "headline": "ID Test"
            }}
            </script>
            <!-- No data-story-id meta tag -->
        </head>
        <body class="hyphenate">
            <h1>ID Test</h1>
            <p class="hyphenate">Content here.</p>
        </body>
    </html>
    """
    # URL ends with alphanumeric ID
    request = Request(url="https://wiadomosci.onet.pl/kraj/tytul/abc123xyz")
    response = HtmlResponse(url="https://wiadomosci.onet.pl/kraj/tytul/abc123xyz", request=request, body=html.encode('utf-8'))
    
    results = list(spider.parse_item(response))
    assert len(results) == 1
    # ID should be extracted from URL regex
    assert results[0]['id'] == "abc123xyz"

def test_parse_item_author_fallback_chain(spider):
    """Test the author fallback chain (3 different selectors)."""
    today_date = datetime.now().strftime('%Y-%m-%d')
    # Test with second fallback selector
    html = f"""
    <html>
        <head>
            <script type="application/ld+json">
            {{
                "datePublished": "{today_date}T12:00:00+01:00"
            }}
            </script>
        </head>
        <body class="hyphenate">
            <h1>Author Test</h1>
            <span class="ods-m-author-xl__name">Second Fallback Author</span>
            <p class="hyphenate">Content.</p>
        </body>
    </html>
    """
    request = Request(url="https://wiadomosci.onet.pl/author-test")
    response = HtmlResponse(url="https://wiadomosci.onet.pl/author-test", request=request, body=html.encode('utf-8'))
    
    results = list(spider.parse_item(response))
    assert len(results) == 1
    assert results[0]['author'] == "Second Fallback Author"

def test_parse_item_image_fallback(spider):
    """Test that image URL is extracted from og:image meta tag."""
    html = """
    <html>
        <head>
            <meta property="og:image" content="http://example.com/fallback.jpg">
            <!-- No JSON-LD image -->
        </head>
        <body class="hyphenate">
            <h1>Image Test</h1>
            <!-- Date needed to pass recent filter -->
            <span class="ods-m-date-authorship__publication">{0} 12:00</span>
            <p>Content must be longer than thirty characters to pass the dumb filter.</p>
        </body>
    </html>
    """.format(datetime.now().strftime('%Y-%m-%d'))
    request = Request(url="https://wiadomosci.onet.pl/image-test")
    response = HtmlResponse(url="https://wiadomosci.onet.pl/image-test", request=request, body=html.encode('utf-8'))
    
    results = list(spider.parse_item(response))
    assert len(results) == 1
    assert results[0]['image_url'] == "http://example.com/fallback.jpg"

def test_parse_item_deep_fallbacks(spider):
    """Test specific 3rd/4th level fallbacks (authorName class, span.date)."""
    today_date = datetime.now().strftime('%Y-%m-%d')
    html = f"""
    <html>
        <head></head>
        <body class="hyphenate">
            <h1>Deep Fallback Test</h1>
            <!-- Date fallback: span with class 'date' -->
            <span class="date">{today_date} 15:00</span>
            <!-- Author fallback: class 'authorName' -->
            <div class="authorName">Deep Author</div>
            <p>Content must be longer than thirty characters to pass the dumb filter in fallback test.</p>
        </body>
    </html>
    """
    request = Request(url="https://wiadomosci.onet.pl/deep-fallback")
    response = HtmlResponse(url="https://wiadomosci.onet.pl/deep-fallback", request=request, body=html.encode('utf-8'))
    
    results = list(spider.parse_item(response))
    assert len(results) == 1
    item = results[0]
    
    assert item['author'] == "Deep Author"
    assert item['date'] == today_date


