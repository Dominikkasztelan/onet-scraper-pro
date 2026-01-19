
from curl_cffi.requests import AsyncSession
from scrapy.http import HtmlResponse
from typing import Optional

class AsyncCurlMiddleware:
    """
    Middleware to bypass anti-bot protections using curl_cffi.
    Features TLS fingerprint impersonation with round-robin profile rotation.
    """
    
    BROWSER_PROFILES = [
        # Chrome Desktop
        "chrome110", "chrome116", "chrome119", "chrome120",
        "chrome123", "chrome124", "chrome131",
        # Chrome Android
        "chrome99_android", "chrome131_android",
        # Safari
        "safari15_3", "safari15_5", "safari17_0", "safari17_2_ios",
        "safari18_0", "safari18_0_ios",
        # Edge
        "edge99", "edge101",
    ]
    
    def __init__(self):
        self._profile_index = 0
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls()
    
    def _get_next_profile(self) -> str:
        """Round-robin profile selection."""
        profile = self.BROWSER_PROFILES[self._profile_index]
        self._profile_index = (self._profile_index + 1) % len(self.BROWSER_PROFILES)
        return profile

    async def process_request(self, request, spider) -> Optional[HtmlResponse]:
        if 'onet.pl' in request.url:
            profile = self._get_next_profile()
            spider.logger.debug(f"AsyncCurlMiddleware: [{profile}] {request.url}")
            
            try:
                async with AsyncSession(impersonate=profile) as session:
                    response = await session.get(request.url)
                    
                    return HtmlResponse(
                        url=request.url,
                        status=response.status_code,
                        body=response.content,
                        encoding='utf-8',
                        request=request
                    )
            except Exception as e:
                spider.logger.error(f"AsyncCurlMiddleware Error: {e}")
                return None
                
        return None
