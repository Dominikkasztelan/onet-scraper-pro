import json
from datetime import datetime
from typing import Any

from scrapy.exceptions import DropItem


class JsonWriterPipeline:
    def __init__(self):
        self.file = None
        self.filename = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls()

    def open_spider(self, spider: Any) -> None:
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            self.filename = f"data_{timestamp}.jsonl"
            self.file = open(self.filename, "w", encoding="utf-8")
            spider.logger.info(f"Saving data to {self.filename}")
        except Exception as e:
            spider.logger.error(f"Failed to open file {self.filename}: {e}")
            self.file = None

    def close_spider(self, spider: Any) -> None:
        if self.file:
            try:
                self.file.close()
            except Exception as e:
                spider.logger.error(f"Error closing file: {e}")

    def process_item(self, item: Any, spider: Any) -> Any:
        if not self.file:
            # If file failed to open, we can't save but we shouldn't crash the spider?
            # Or maybe we should drop the item to signal it wasn't saved?
            spider.logger.warning(f"Item not saved (file closed): {item.get('url')}")
            return item

        try:
            # item can be a dict or Scrapy Item
            item_dict = item if isinstance(item, dict) else dict(item)
            line = json.dumps(item_dict, ensure_ascii=False) + "\n"
            self.file.write(line)
        except Exception as e:
            spider.logger.error(f"Error writing item to file: {e}")
            # Optionally drop item or raise generic error
        
        return item
