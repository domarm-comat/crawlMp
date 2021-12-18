__version__ = "0.3.1"

from multiprocessing import Manager

share_manager = Manager()


class CrawlException(Exception):
    ...


class ActionException(Exception):
    ...
