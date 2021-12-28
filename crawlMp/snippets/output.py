from typing import Optional

from crawlMp.results import Results


def print_summary(results: Optional[Results] = None) -> None:
    """
    Print summary of collected results.
    :param results:
    :return: None
    """
    if results is not None:
        print(f"Crawled in: {round(results.duration, 2)} s")
        print(f"Number of hits: {len(results.hits)}")
        print(f"Number of followed links: {len(results.links_followed)}")
        print(f"Number of skipped links: {len(results.links_skipped)}")
    else:
        print("No results...")


def print_list(results: Optional[Results] = None) -> None:
    """
    Print every hit on a new line.
    Suitable for bash output.
    :param results:
    :return: None
    """
    if results is not None and len(results.hits) > 0:
        print(*[result[0] for result in results.hits], sep="\n")
