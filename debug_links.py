import urllib.request
from scrapy.linkextractors import LinkExtractor
from scrapy.http import HtmlResponse

url = 'https://wiadomosci.onet.pl/'
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as f:
        body = f.read()
    response = HtmlResponse(url=url, body=body)
    
    le = LinkExtractor(allow=(r'wiadomosci\.onet\.pl/[a-z-]+/[a-z0-9-]+/[a-z0-9]+'), deny=(r'#', r'autorzy'), unique=True)
    links = le.extract_links(response)
    
    print(f"Found {len(links)} matching links.")
    for link in links[:5]:
        print(f"Match: {link.url}")
        
    # Check what non-matching links look like
    all_le = LinkExtractor()
    all_links = all_le.extract_links(response)
    print(f"\nTotal links found: {len(all_links)}")
    print("Sample of first 5 links:")
    for link in all_links[:5]:
        print(f"Link: {link.url}")

except Exception as e:
    print(f"Error: {e}")
