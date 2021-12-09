__version__ = "0.2.5"

from multiprocessing import Manager
from time import time

start_time = time()
share_manager = Manager()


class CrawlException(Exception):
    ...
