__version__ = "0.3.1"

from multiprocessing import Manager
from time import time

share_manager = Manager()


class CrawlException(Exception):
    ...


class ActionException(Exception):
    ...
