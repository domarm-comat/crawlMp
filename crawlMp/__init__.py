__version__ = "0.3.0"

from multiprocessing import Manager
from time import time

start_time = time()
share_manager = Manager()


class CrawlException(Exception):
    ...


class ActionException(Exception):
    ...
