import argparse
from time import time_ns

from dataCrawler.backend.dirCrawler import DirCrawler
from dataCrawler.backend.interfaces.crawlerManager import CrawlerManager
from dataCrawler.snippets.output import print_results_summary

parser = argparse.ArgumentParser()
parser.add_argument("--entrypoint")
parser.add_argument("--processes", default=4, type=int)
parser.add_argument("--buffer_size", default=64, type=int)
args = parser.parse_args()

start_time = time_ns()
results = None
if args.processes == 1:
    for results in DirCrawler(args.entrypoint):
        pass
else:
    def done(crawler_results):
        print_results_summary(start_time, crawler_results)


    manager = CrawlerManager(DirCrawler, links=[args.entrypoint], num_proc=args.processes, buffer_size=args.buffer_size)
    manager.start(done)