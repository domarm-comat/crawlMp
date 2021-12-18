from time import time

from crawlMp.results import Results


def print_summary(results: Results = None, start_time: float = None) -> None:
    """
    Print summary of collected results.
    :param Results results:
    :param float start_time:
    :return: None
    """
    if results is not None:
        if start_time is not None:
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
    :param Results results:
    :return: float None
    """
    if len(results.hits) > 0:
        print(*[result[0] for result in results.hits], sep="\n")
