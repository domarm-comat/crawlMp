import argparse
import re
from time import time_ns

from crawlMp.sources.fileCrawler import FileSearchCrawler
from crawlMp.sources.interfaces.crawlerManager import CrawlerManager
from crawlMp.snippets.output import print_results_summary

parser = argparse.ArgumentParser()
parser.add_argument("--entrypoint")
parser.add_argument("--processes", default=8, type=int)
parser.add_argument("--search_pattern", default="\.zip$", type=str)
parser.add_argument("--buffer_size", default=64, type=int)
args = parser.parse_args()

start_time = time_ns()
results = None
search_pattern = re.compile(args.search_pattern)


def done(crawler_results):
    print_results_summary(start_time, crawler_results)


if args.processes == 1:
    results = None
    for results in FileSearchCrawler(args.entrypoint, search_pattern):
        pass
    done(results)
else:
    manager = CrawlerManager(FileSearchCrawler, links=[args.entrypoint], num_proc=args.processes,
                             buffer_size=args.buffer_size, search_pattern=search_pattern)
    manager.start(done)
