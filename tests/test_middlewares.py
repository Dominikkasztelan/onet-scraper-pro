
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from scrapy.http import Request, HtmlResponse
from onet_scraper.middlewares import AsyncCurlMiddleware

@pytest.fixture
def middleware():
    return AsyncCurlMiddleware()

@pytest.fixture
def spider():
    mock_spider = MagicMock()
    mock_spider.logger = MagicMock()
    return mock_spider

def test_from_crawler_factory():
    """Verify from_crawler factory method works."""
    crawler = MagicMock()
    middleware = AsyncCurlMiddleware.from_crawler(crawler)
    assert isinstance(middleware, AsyncCurlMiddleware)
    assert middleware._profile_index == 0


@pytest.mark.asyncio
async def test_process_request_intercepts_onet(middleware, spider):
    request = Request(url="https://wiadomosci.onet.pl/artykul")
    
    mock_session = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b"<html>Test Content</html>"
    
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)
    mock_session.get = AsyncMock(return_value=mock_response)

    with patch('onet_scraper.middlewares.AsyncSession', return_value=mock_session):
        result = await middleware.process_request(request, spider)
        
        assert isinstance(result, HtmlResponse)
        assert result.body == b"<html>Test Content</html>"
        assert result.status == 200

@pytest.mark.asyncio
async def test_process_request_ignores_other_domains(middleware, spider):
    request = Request(url="https://google.com")
    
    with patch('onet_scraper.middlewares.AsyncSession') as mock_session_cls:
        result = await middleware.process_request(request, spider)
        
        mock_session_cls.assert_not_called()
        assert result is None

@pytest.mark.asyncio
async def test_process_request_handles_exception(middleware, spider):
    request = Request(url="https://wiadomosci.onet.pl/error")
    
    mock_session = MagicMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)
    mock_session.get = AsyncMock(side_effect=Exception("Curl Error"))

    with patch('onet_scraper.middlewares.AsyncSession', return_value=mock_session):
        result = await middleware.process_request(request, spider)
        
        spider.logger.error.assert_called()
        assert result is None

@pytest.mark.asyncio
async def test_profile_rotation(middleware, spider):
    """Verify that profiles rotate in round-robin fashion."""
    request = Request(url="https://wiadomosci.onet.pl/test")
    
    mock_session = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b"<html></html>"
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)
    mock_session.get = AsyncMock(return_value=mock_response)

    profiles_used = []
    
    def capture_profile(*args, **kwargs):
        profiles_used.append(kwargs.get('impersonate'))
        return mock_session
    
    with patch('onet_scraper.middlewares.AsyncSession', side_effect=capture_profile):
        # Make 3 requests
        for _ in range(3):
            await middleware.process_request(request, spider)
    
    # Verify different profiles were used (matches updated list)
    assert profiles_used[0] == "chrome110"
    assert profiles_used[1] == "chrome116"
    assert profiles_used[2] == "chrome119"
    # All should be different
    assert len(set(profiles_used)) == 3
