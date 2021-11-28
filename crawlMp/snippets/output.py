from multiprocessing.managers import BaseProxy
from time import time_ns

from crawlMp import start_time
from crawlMp.sources.results import Results


def print_summary(results: Results = None) -> None:
    """
    Print summary of collected results.
    :param results:
    :return: None
    """
    if results is not None:
        print(f"Crawled in: {(time_ns() - start_time) * 1e-9} s")
        for key in results.fields:
            value = results.__getattribute__(key)
            if isinstance(value, (list, tuple, BaseProxy)):
                print(f"Number of {key}: {len(value)}")
    else:
        print("No results...")


def print_list(results: Results = None) -> None:
    """
    Print every target result in new line.
    Suitable for bash output.
    :param results:
    :return: None
    """
    print(*results.targets_found, sep="\n")
