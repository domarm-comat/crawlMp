from multiprocessing import Manager
from time import time, time_ns, sleep

from dataCrawler.backend.dirCrawler import DirCrawler
from dataCrawler.backend.interfaces.crawlerManager import CrawlWorker, CrawlerManager


a = time_ns()

# print(DirCrawler)

# for crawler in DirCrawler("/home/domarm"):
#     ...
# for crawler in DirCrawlerMp("/home/domarm", num_proc=8):
#     ...
# crawler = DirCrawlerMp("/home/domarm", num_proc=8)
# crawler.crawl_async()

# print(len(crawler.targets))
manager = CrawlerManager(DirCrawler, links=["/"], num_proc=8)
manager.start()

print((time_ns() - a) * 1e-9)