from time import time_ns

from dataCrawler.backend.dirCrawler import DirCrawler
from dataCrawler.backend.interfaces.crawlerManager import CrawlerManager

a = time_ns()

# print(DirCrawler)

# for crawler in DirCrawler("/home/domarm"):
#     ...
# for crawler in DirCrawlerMp("/home/domarm", num_proc=8):
#     ...
# crawler = DirCrawlerMp("/home/domarm", num_proc=8)
# crawler.crawl_async()

# print(len(crawler.targets))
manager = CrawlerManager(DirCrawler, links=["/"], num_proc=8, buffer_size=64)
results = manager.start()
print(len(results["targets"]))

# for worker in manager.workers:
#     print(worker.crawler)

print((time_ns() - a) * 1e-9)
