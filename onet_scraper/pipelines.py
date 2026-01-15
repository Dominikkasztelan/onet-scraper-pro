import json
from datetime import datetime

class JsonWriterPipeline:
    def open_spider(self, spider):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.filename = f'data_{timestamp}.jsonl'
        self.file = open(self.filename, 'w', encoding='utf-8')
        spider.logger.info(f"Saving data to {self.filename}")

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(item, ensure_ascii=False) + "\n"
        self.file.write(line)
        return item