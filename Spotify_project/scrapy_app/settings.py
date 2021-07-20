import os

from scrapy_app.utils.logging import configure_console_logging, configure_file_logging

# crawling settings
ITEM_PIPELINES = {
    # 'scrapy_app.pipelines.LoggingPipeline': 100,
    'scrapy_app.pipelines.CsvOnClosePipeline': 700,
}
# LOG_LEVEL = 'INFO'
# CONCURRENT_REQUESTS = CONCURRENT_REQUESTS_PER_DOMAIN = 10


# directories
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_DIR = os.path.join(PROJECT_DIR, 'results')
RESOURCES_DIR = os.path.join(PROJECT_DIR, 'etc', 'resources')
LOG_DIR = os.path.join(PROJECT_DIR, 'etc', 'logs')


# standard settings
SPIDER_MODULES = ['scrapy_app.spiders']
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'


# logging settings
LOG_LEVEL = 'INFO'
configure_console_logging(level=LOG_LEVEL)
configure_file_logging(level='DEBUG', file_name='log.txt', mode='w')
configure_file_logging(level='WARNING', file_name='log_error.txt', mode='a')
