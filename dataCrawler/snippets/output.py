from time import time_ns


def print_results_summary(start_time, results=None):
    if results is not None:
        print(f"Crawled in: {(time_ns() - start_time) * 1e-9} ms")
        print(f"Number of results: {len(results.targets)}")
        print(f"Number of followed links: {len(results.links_followed)}")
        print(f"Number of errors: {len(results.links_error)}")
    else:
        print("No results...")