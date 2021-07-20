import os
import sys

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# change working dir to project dir
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(project_dir)
sys.path.append(project_dir)


def crawl(spider, **kwargs):
    process = CrawlerProcess(get_project_settings(), install_root_handler=False)
    process.crawl(spider, **kwargs)
    process.start()


def crawl_many(*spiders):
    process = CrawlerProcess(get_project_settings(), install_root_handler=False)
    for spider in spiders:
        process.crawl(spider)
    process.start()
