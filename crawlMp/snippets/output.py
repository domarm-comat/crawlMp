from time import time

from crawlMp import start_time
from crawlMp.results import Results


def print_summary(results: Results = None) -> None:
    """
    Print summary of collected results.
    :param results:
    :return: None
    """
    if results is not None:
        print(f"Crawled in: {round(time() - start_time, 2)} s")
        print(f"Number of hits: {len(results.hits)}")
        print(f"Number of followed links: {len(results.links_followed)}")
        print(f"Number of skipped links: {len(results.links_skipped)}")
    else:
        print("No results...")


def print_list(results: Results = None) -> None:
    """
    Print every hit on a new line.
    Suitable for bash output.
    :param results:
    :return: None
    """
    if len(results.hits) > 0:
        print(*[result for result in results.hits], sep="\n")
