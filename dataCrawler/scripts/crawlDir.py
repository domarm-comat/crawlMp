import argparse
from time import time_ns

from dataCrawler.backend.dirCrawler import DirCrawler
from dataCrawler.backend.interfaces.crawlerManager import CrawlerManager

parser = argparse.ArgumentParser()
parser.add_argument("--entrypoint")
parser.add_argument("--processes", default=4, type=int)
parser.add_argument("--buffer_size", default=64, type=int)
args = parser.parse_args()
a = time_ns()

if args.processes == 1:
    for crawler in DirCrawler(args.entrypoint):
        ...
    results = {"targets": crawler.targets,
               "links_followed": crawler.links_followed,
               "links_error": crawler.links_error}
else:
    manager = CrawlerManager(DirCrawler, links=[args.entrypoint], num_proc=args.processes, buffer_size=args.buffer_size)
    results = manager.start()

print(f"Crawled in: {(time_ns() - a) * 1e-9} ms")
print(f"Number of results: {len(results['targets'])}")
print(f"Number of followed links: {len(results['links_followed'])}")
print(f"Number of errors: {len(results['links_error'])}")
