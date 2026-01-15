from scrapy.cmdline import execute
import sys
import os

if __name__ == '__main__':
    # Add the project root to the python path
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    # Run the spider 'onet' with DEBUG log level
    # This is equivalent to running: scrapy crawl onet -L DEBUG
    try:
        execute(['scrapy', 'crawl', 'onet', '-L', 'DEBUG'])
    except SystemExit:
        pass
