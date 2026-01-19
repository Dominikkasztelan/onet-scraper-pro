
import pytest
from onet_scraper.items import ArticleItem

def test_article_item_validation():
    # Valid item
    item = ArticleItem(
        title="Valid Title",
        url="http://onet.pl/valid",
        date="2026-01-01",
        lead="Some lead",
        content="Some content",
        id="123"
    )
    assert item.title == "Valid Title"

def test_article_item_titles_empty():
    with pytest.raises(ValueError):
        ArticleItem(
            title="",
            url="http://onet.pl/valid",
            date="2026-01-01"
        )

def test_article_item_url_invalid():
    with pytest.raises(ValueError):
        ArticleItem(
            title="Title",
            url="ftp://invalid-url.com",
            date="2026-01-01"
        )

def test_article_item_title_whitespace_only():
    """Title with only whitespace should be rejected."""
    with pytest.raises(ValueError):
        ArticleItem(
            title="   ",
            url="http://onet.pl/valid",
            date="2026-01-01"
        )

def test_article_item_url_https():
    """HTTPS URLs should be valid."""
    item = ArticleItem(
        title="Title",
        url="https://onet.pl/article",
        date="2026-01-01"
    )
    assert item.url == "https://onet.pl/article"

def test_article_item_optional_fields():
    """All optional fields should accept None."""
    item = ArticleItem(
        title="Title",
        url="http://onet.pl/valid",
        date="2026-01-01"
        # All other fields default to None
    )
    assert item.lead is None
    assert item.content is None
    assert item.author is None
    assert item.keywords is None
    assert item.section is None
    assert item.read_time is None

def test_article_item_title_strips_whitespace():
    """Title should be stripped of leading/trailing whitespace."""
    item = ArticleItem(
        title="  Title with spaces  ",
        url="http://onet.pl/valid",
        date="2026-01-01"
    )
    assert item.title == "Title with spaces"

def test_article_item_read_time_positive():
    """Read time should accept positive integers."""
    item = ArticleItem(
        title="Title",
        url="http://onet.pl/valid",
        date="2026-01-01",
        read_time=5
    )
    assert item.read_time == 5
