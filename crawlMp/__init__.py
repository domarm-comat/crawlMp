__version__ = "0.3.3"

from multiprocessing import Manager

share_manager = Manager()


class CrawlException(Exception):
    ...


class ActionException(Exception):
    ...
