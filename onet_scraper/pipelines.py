import json
from datetime import datetime
from typing import Any

class JsonWriterPipeline:
    def __init__(self):
        self.file = None
        self.filename = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls()

    def open_spider(self, spider: Any) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.filename = f'data_{timestamp}.jsonl'
        self.file = open(self.filename, 'w', encoding='utf-8')
        spider.logger.info(f"Saving data to {self.filename}")

    def close_spider(self, spider: Any) -> None:
        if self.file:
            self.file.close()

    def process_item(self, item: Any, spider: Any) -> Any:
        # Note: 'spider' argument is still required by Scrapy interface for now, 
        # even if warnings say otherwise, removing it breaks the interface. 
        # The warning is about *relying* on it for things available in crawler.
        # But for simple logging/access, it's standard. 
        # Actually the warning said: "requires a spider argument, this is deprecated" 
        # leading to confusion. 
        # Scrapy core code: call(method, item=item, spider=spider)
        # We will keep the signature standard. The warning might be internal or related to how it's called.
        # Let's verify exact warning content: "UrllibDownloaderMiddleware.process_request() requires a spider argument..."
        # Wait, if I change signature to not have spider, it fails.
        # The warning typically means: "You are defining it with spider, but we want you to use crawler context".
        # However, for Pipelines, open_spider(self, spider) IS the standard API.
        # Let's look closer at the log: "...requires a spider argument... argument will not be passed in future".
        # Correct fix is often to use from_crawler to get what you need.
        if self.file:
            line = json.dumps(item, ensure_ascii=False) + "\n"
            self.file.write(line)
        return item