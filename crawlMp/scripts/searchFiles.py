#!/usr/bin/env python3
import argparse

from crawlMp.constants import *
from crawlMp.snippets.output import print_summary, print_list
from crawlMp.sources.crawlMp import CrawlMp
from crawlMp.sources.fileCrawler import FileSearchCrawler
from crawlMp.sources.results import Results

parser = argparse.ArgumentParser()
parser.add_argument("-l", "--links", type=str, nargs="+", help="Entry points to start search", required=True)
parser.add_argument("-o", "--output", default=[OUTPUT_LIST], type=str, nargs="+",
                    choices=[OUTPUT_SUMMARY, OUTPUT_LIST],
                    help=f"Entry points to start search")
parser.add_argument("-np", "--processes", default=8, type=int, help="Number of processes used, minimum is 1")
parser.add_argument("-s", "--search", default=".", type=str, help="RegExp filename pattern to search for")
parser.add_argument("-bs", "--buffer_size", default=64, type=int, help="Buffer links size, only used if processes > 1")
args = parser.parse_args()


def on_done(crawler_results: Results) -> None:
    for output_mode in args.output:
        if output_mode == OUTPUT_SUMMARY:
            print_summary(crawler_results)
        elif output_mode == OUTPUT_LIST:
            print_list(crawler_results)


if args.processes == 1:
    results = None
    for results in FileSearchCrawler(args.links, args.search):
        pass
    on_done(results.get_results())
else:
    manager = CrawlMp(FileSearchCrawler, links=args.links, num_proc=args.processes,
                      buffer_size=args.buffer_size, pattern=args.search)
    manager.start(on_done)
