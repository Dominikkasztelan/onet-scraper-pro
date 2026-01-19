
import pytest
from unittest.mock import patch, mock_open
from onet_scraper.utils.text_cleaners import clean_article_content

# Mock rules to avoid depending on file system/json loading during unit test logic
MOCK_RULES = {
    "scam_phrases": ["CLICK HERE", "BUY NOW"],
    "cutoff_markers": ["READ MORE"]
}

@pytest.fixture
def mock_rules():
    with patch('onet_scraper.utils.text_cleaners.RULES', MOCK_RULES):
        yield

def test_clean_article_content_basic(mock_rules):
    raw = [
        "  Title  ",
        "Introduction paragraph.",
        "   ", # Empty line
        "Content."
    ]
    result = clean_article_content(raw)
    assert "Title" in result
    assert "Introduction paragraph." in result
    assert "Content." in result
    assert "\n\n" not in result # Empty line removed

def test_clean_article_content_removes_scam(mock_rules):
    raw = [
        "Normal content",
        "This is a scam CLICK HERE to win",
        "More normal content"
    ]
    result = clean_article_content(raw)
    assert "Normal content" in result
    assert "CLICK HERE" not in result
    assert "More normal content" in result

def test_clean_article_content_cutoff(mock_rules):
    raw = [
        "Start of article",
        "Middle part",
        "READ MORE below",
        "This should be cut off"
    ]
    result = clean_article_content(raw)
    assert "Start of article" in result
    assert "Middle part" in result
    assert "READ MORE" not in result
    assert "This should be cut off" not in result

def test_clean_article_content_empty_input():
    assert clean_article_content([]) == ""
    # Note: clean_article_content expects list[str], passing None will cause TypeError
    # This is by design - type hints indicate list[str] is required
    # If None handling is needed, the function should be modified

def test_clean_article_content_whitespace_only(mock_rules):
    """Test that lines with only whitespace are removed."""
    raw = [
        "   ",
        "\t\t",
        "\n",
        "Actual content here"
    ]
    result = clean_article_content(raw)
    assert result == "Actual content here"

def test_clean_article_content_short_lines(mock_rules):
    """Test that very short lines (< 3 chars) are filtered out."""
    raw = [
        "OK",  # 2 chars - should be filtered
        "Yes",  # 3 chars - should be kept
        "This is a longer line"
    ]
    result = clean_article_content(raw)
    assert "OK" not in result
    assert "Yes" in result
    assert "This is a longer line" in result
