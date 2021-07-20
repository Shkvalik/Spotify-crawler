import logging
import os
import pathlib


def configure_console_and_file_logging(console_level='INFO', file_level='DEBUG', file_name='log.txt', file_mode='a'):
    # from scrapy.utils.log import configure_logging
    # configure_logging(install_root_handler=False, settings={'LOG_LEVEL': 'INFO'})
    configure_console_logging(level=console_level)
    configure_file_logging(level=file_level, file_name=file_name, mode=file_mode)


def configure_console_logging(level):
    from scrapy.utils.log import configure_logging
    configure_logging(install_root_handler=True, settings={'LOG_LEVEL': level})


def configure_file_logging(level, file_name='log.txt', mode='w'):
    """configure logging to file"""
    from scrapy_app.settings import LOG_DIR
    pathlib.Path(LOG_DIR).mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    file_logger = logging.FileHandler(filename=os.path.join(LOG_DIR, file_name), mode=mode, encoding='utf-8')
    file_logger.setLevel(level)
    file_logger.setFormatter(formatter)
    logging.getLogger().addHandler(file_logger)
