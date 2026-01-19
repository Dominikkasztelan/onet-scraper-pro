
import pytest
import asyncio
from unittest.mock import MagicMock, patch, call
from scrapy.http import Request, HtmlResponse
from onet_scraper.middlewares import UrllibDownloaderMiddleware
import urllib.error

@pytest.fixture
def middleware():
    return UrllibDownloaderMiddleware(user_agent='TestUserAgent/1.0')

@pytest.fixture
def spider():
    mock_spider = MagicMock()
    mock_spider.logger = MagicMock()
    # Settings no longer needed here for UA, handled in init/from_crawler
    return mock_spider

def test_process_request_intercepts_onet(middleware, spider):
    request = Request(url="https://wiadomosci.onet.pl/artykul")
    
    # Context Manager mock for urlopen
    with patch('urllib.request.urlopen') as mock_urlopen:
        # Mock the context manager behavior of urlopen
        mock_response = MagicMock()
        mock_response.read.return_value = b"<html>Test Content</html>"
        mock_response.geturl.return_value = "https://wiadomosci.onet.pl/artykul"
        mock_response.status = 200
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        # Run async method
        result = asyncio.run(middleware.process_request(request, spider))
        
        # Verify it was called
        mock_urlopen.assert_called_once()
        # Verify it returns a Scrapy Response
        assert isinstance(result, HtmlResponse)
        assert result.body == b"<html>Test Content</html>"
        assert result.status == 200
        # Check logs (Debug level now)
        spider.logger.debug.assert_any_call("UrllibMiddleware: Intercepting https://wiadomosci.onet.pl/artykul")

def test_process_request_ignores_other_domains(middleware, spider):
    request = Request(url="https://google.com")
    
    with patch('urllib.request.urlopen') as mock_urlopen:
        result = asyncio.run(middleware.process_request(request, spider))
        
        # Should NOT call urllib
        mock_urlopen.assert_not_called()
        # Should return None (continue chain)
        assert result is None

def test_process_request_handles_exception(middleware, spider):
    request = Request(url="https://wiadomosci.onet.pl/error")
    
    with patch('urllib.request.urlopen') as mock_urlopen:
        # Make urlopen raise an arbitrary exception
        mock_urlopen.side_effect = urllib.error.URLError(reason="Connection Refused")
        
        result = asyncio.run(middleware.process_request(request, spider))
        
        # Should log error
        spider.logger.error.assert_called()
        # Should return None to let Scrapy retry naturally
        assert result is None

def test_process_request_uses_user_agent(middleware, spider):
    """Verify that User-Agent from init is used in the request."""
    request = Request(url="https://wiadomosci.onet.pl/artykul")
    
    with patch('urllib.request.urlopen') as mock_urlopen, \
         patch('urllib.request.Request') as mock_request_class:
        mock_response = MagicMock()
        mock_response.read.return_value = b"<html>Content</html>"
        mock_response.geturl.return_value = "https://wiadomosci.onet.pl/artykul"
        mock_response.status = 200
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        asyncio.run(middleware.process_request(request, spider))
        
        # Verify Request was created with correct User-Agent header
        mock_request_class.assert_called_once()
        call_args = mock_request_class.call_args
        headers = call_args[1]['headers'] if 'headers' in call_args[1] else call_args[0][1] if len(call_args[0]) > 1 else {}
        # The headers dict should contain User-Agent set in fixture
        assert headers.get('User-Agent') == 'TestUserAgent/1.0'

def test_process_request_handles_oserror(middleware, spider):
    """Test that OSError (network issues) is handled gracefully."""
    request = Request(url="https://wiadomosci.onet.pl/network-error")
    
    with patch('urllib.request.urlopen') as mock_urlopen:
        mock_urlopen.side_effect = OSError("Network unreachable")
        
        result = asyncio.run(middleware.process_request(request, spider))
        
        assert result is None
        spider.logger.error.assert_called()

def test_process_request_subdomain_matching(middleware, spider):
    """Test that subdomains of onet.pl are also intercepted."""
    request = Request(url="https://sport.onet.pl/artykul")
    
    with patch('urllib.request.urlopen') as mock_urlopen:
        mock_response = MagicMock()
        mock_response.read.return_value = b"<html>Sport</html>"
        mock_response.geturl.return_value = "https://sport.onet.pl/artykul"
        mock_response.status = 200
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        result = asyncio.run(middleware.process_request(request, spider))
        
        # Should intercept sport.onet.pl as well
        mock_urlopen.assert_called_once()
        assert isinstance(result, HtmlResponse)
