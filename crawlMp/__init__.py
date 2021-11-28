from multiprocessing import Manager
from time import time_ns

start_time = time_ns()
share_manager = Manager()


class CrawlException(Exception):
    ...
