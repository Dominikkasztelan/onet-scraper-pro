
import json
from datetime import datetime

from scrapy.http import Response
from typing import Optional, Dict, Any

def extract_json_ld(response: Response) -> Dict[str, Optional[str]]:
    """
    Extracts relevant metadata (date, author, section) from JSON-LD scripts.
    Returns a dictionary with found keys.
    """
    ld_json_scripts = response.xpath('//script[@type="application/ld+json"]/text()').getall()
    metadata: Dict[str, Optional[str]] = {
        'datePublished': None,
        'dateModified': None,
        'author': None,
        'articleSection': None,
        'image_url': None
    }

    found = False
    
    for script in ld_json_scripts:
        try:
            data = json.loads(script)
            
            def process_node(node: Dict[str, Any]) -> None:
                nonlocal found
                updates: Dict[str, Optional[str]] = {}
                if 'datePublished' in node:
                    updates['datePublished'] = node['datePublished']
                    found = True
                if 'dateModified' in node:
                    updates['dateModified'] = node['dateModified']
                if 'author' in node:
                    if isinstance(node['author'], dict) and 'name' in node['author']:
                        updates['author'] = node['author']['name']
                    elif isinstance(node['author'], list) and len(node['author']) > 0 and 'name' in node['author'][0]:
                        updates['author'] = node['author'][0]['name']
                if 'articleSection' in node:
                    updates['articleSection'] = node['articleSection']
                if 'image' in node:
                    if isinstance(node['image'], dict) and 'url' in node['image']:
                        updates['image_url'] = node['image']['url']
                    elif isinstance(node['image'], str):
                        updates['image_url'] = node['image']
                
                # Update only if not already set (or overwrite? usually first is best)
                for k, v in updates.items():
                    if not metadata[k]:
                        metadata[k] = v

            if '@graph' in data:
                for node in data['@graph']:
                    process_node(node)
            else:
                process_node(data)
            
            # if found: break  <-- Removed to allow gathering metadata from multiple scripts
            pass
        except (json.JSONDecodeError, ValueError, TypeError):
            continue
            
    return metadata

def parse_is_recent(date_str: str, days_limit: int = 3) -> bool:
    """
    Checks if a date string (YYYY-MM-DD...) is within the last `days_limit` days.
    """
    if not date_str:
        return False
    try:
        if 'T' in date_str:
            date_str = date_str.split('T')[0]
        else:
            date_str = date_str[:10]
            
        article_date = datetime.strptime(date_str, '%Y-%m-%d')
        today = datetime.now()
        days_diff = (today - article_date).days
        return 0 <= days_diff <= days_limit
    except ValueError:
        return False
