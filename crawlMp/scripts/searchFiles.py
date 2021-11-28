import argparse
import re
from time import time_ns

from crawlMp.sources.fileCrawler import FileSearchCrawler
from crawlMp.sources.crawlerManager import CrawlerManager
from crawlMp.snippets.output import print_results_summary

parser = argparse.ArgumentParser()
parser.add_argument("--links", type=str, nargs="+", help="Entry points to start search")
parser.add_argument("--processes", default=8, type=int, help="Number of processes used, minimum is 1")
parser.add_argument("--search_pattern", default=".", type=str, help="RegExp filename pattern to search for")
parser.add_argument("--buffer_size", default=64, type=int, help="Buffer links size, only used if processes > 1")
args = parser.parse_args()

start_time = time_ns()
results = None
search_pattern = re.compile(args.search_pattern)


def done(crawler_results):
    print_results_summary(start_time, crawler_results)


if args.processes == 1:
    results = None
    for results in FileSearchCrawler(args.links, search_pattern):
        pass
    done(results)
else:
    manager = CrawlerManager(FileSearchCrawler, links=args.links, num_proc=args.processes,
                             buffer_size=args.buffer_size, search_pattern=search_pattern)
    manager.start(done)
