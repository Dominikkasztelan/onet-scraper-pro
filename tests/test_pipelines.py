
import pytest
from unittest.mock import MagicMock, patch, mock_open
from onet_scraper.pipelines import JsonWriterPipeline
import json

@pytest.fixture
def pipeline():
    return JsonWriterPipeline()

@pytest.fixture
def spider():
    mock_spider = MagicMock()
    mock_spider.logger = MagicMock()
    return mock_spider

def test_open_spider_creates_timestamped_file(pipeline, spider):
    # Mock datetime to return a fixed time
    fixed_time = "2026-05-20_12-00-00"
    
    with patch('onet_scraper.pipelines.datetime') as mock_datetime:
        mock_datetime.now.return_value.strftime.return_value = fixed_time
        
        # Mock open
        with patch('builtins.open', mock_open()) as mocked_file:
            pipeline.open_spider(spider)
            
            # Check filename format
            expected_filename = f'data_{fixed_time}.jsonl'
            # Assert file was opened with write mode and correct encoding
            mocked_file.assert_called_once_with(expected_filename, 'w', encoding='utf-8')
            assert pipeline.filename == expected_filename

def test_process_item_writes_jsonl(pipeline, spider):
    # Setup pipeline with a mocked file handle
    mock_file = MagicMock()
    pipeline.file = mock_file
    
    item = {'title': 'Test Title', 'url': 'http://test.com'}
    
    pipeline.process_item(item, spider)
    
    # Verify write call
    # ensure_ascii=False is important for Polish characters
    expected_line = json.dumps(item, ensure_ascii=False) + "\n"
    mock_file.write.assert_called_once_with(expected_line)

def test_close_spider_closes_file(pipeline, spider):
    mock_file = MagicMock()
    pipeline.file = mock_file
    
    pipeline.close_spider(spider)
    
    mock_file.close.assert_called_once()
