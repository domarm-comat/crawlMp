from time import time_ns

from crawlMp import start_time


def print_summary(results=None) -> None:
    """
    Print summary of collected results.
    :param results:
    :return: None
    """
    if results is not None:
        print(f"Crawled in: {(time_ns() - start_time) * 1e-9} s")
        print(f"Number of results: {len(results.targets)}")
        print(f"Number of followed links: {len(results.links_followed)}")
        print(f"Number of errors: {len(results.links_error)}")
    else:
        print("No results...")


def print_results(results=None) -> None:
    """
    Print every result in new line.
    Suitable for bash output.
    :param results:
    :return: None
    """
    print(*results.targets, sep="\n", end="")
