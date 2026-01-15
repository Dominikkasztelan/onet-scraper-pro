import json

class JsonWriterPipeline:
    def open_spider(self, spider):
        self.file = open('data_production.jsonl', 'w', encoding='utf-8')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(item, ensure_ascii=False) + "\n"
        self.file.write(line)
        return item