__version__ = "0.3.6"

from multiprocessing import Manager

share_manager = Manager()


class CrawlException(Exception):
    ...


class ActionException(Exception):
    ...
