import urllib.request
from scrapy.linkextractors import LinkExtractor
from scrapy.http import HtmlResponse

url = 'https://wiadomosci.onet.pl/'
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as f:
        body = f.read()
    response = HtmlResponse(url=url, body=body)
    
    le = LinkExtractor(allow=(r'wiadomosci\.onet\.pl/[a-z0-9-]+/[a-z0-9-]+/[a-z0-9]+'), deny=(r'#', r'autorzy', r'oferta', r'partner', r'reklama', r'promocje', r'sponsored'), unique=True)
    links = le.extract_links(response)
    
    print(f"Found {len(links)} matching links.")
    
    from collections import Counter
    parent_classes = Counter()
    
    for link in links:
        # Find the element in the response that matches the link url
        # This is a bit of an approximation, but good enough for analysis
        # We look for 'a' tags with this href
        a_tags = response.xpath(f'//a[@href="{link.url}"]')
        for a in a_tags:
            # Get parent class
            parent = a.xpath('..')
            p_class = parent.xpath('@class').get()
            if p_class:
                parent_classes[p_class] += 1
            
            # Get grandparent class
            grandparent = parent.xpath('..')
            gp_class = grandparent.xpath('@class').get()
            if gp_class:
                parent_classes[f"GP: {gp_class}"] += 1

    print("\nMost common parent/grandparent classes:")
    for cls, count in parent_classes.most_common(10):
        print(f"{count}: {cls}")

except Exception as e:
    print(f"Error: {e}")
