import os
import pathlib

from scrapy.exporters import CsvItemExporter


class CsvBasePipeline:
    """
    Base class for both versions of CSV spider.
    Version 1 (CsvPipeline): writing each item immediately during scraping
    Version 2 (CsvOnClosePipeline): collecting all items and writing them at once on spider finish
    """
    def __init__(self):
        self.file_path = None   # path of csv file
        self.file = None        # csv file object
        self.exporter = None    # scrapy item exporter object

    def open_file(self, spider):
        """Open CSV file for exporting"""
        csv_dir = spider.settings.get('CSV_DIR')
        pathlib.Path(csv_dir).mkdir(parents=True, exist_ok=True)
        file_path = os.path.join(csv_dir, f'{spider.name}.csv')

        self.file = open(file_path, mode='w+b')
        return CsvItemExporter(self.file, encoding='utf-8-sig')

    def close_file(self):
        """Close CSV file after export"""
        self.file.close()


class CsvPipeline(CsvBasePipeline):
    """
    Pipeline for writing to CSV file, each item immediately during scraping
    """
    def open_spider(self, spider):
        self.exporter = self.open_file(spider)

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

    def close_spider(self, spider):
        self.close_file()


class CsvOnClosePipeline(CsvBasePipeline):
    """
    Pipeline for writing to CSV file, collecting all items and writing them at once on spider finish
    """
    def __init__(self):
        super().__init__()
        self.items = []     # list of all items
        self.fields = []    # list of all fields (used as csv header)

    def process_item(self, item, spider):
        self.items.append(item)
        for field in item:
            self.fields.append(field) if field not in self.fields else None
        return item

    def close_spider(self, spider):
        self.exporter = self.open_file(spider)
        for item in self.items:
            self.exporter.export_item(item)
        self.close_file()


class LoggingPipeline:
    def process_item(self, item, spider):
        spider.logger.info(item)
        return item
