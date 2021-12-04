import math
import os
import re

from crawlMp import CrawlException
from crawlMp.crawlers.crawler import Crawler


class FileCrawler(Crawler):

    def __init__(self, links: list, max_depth: int = math.inf, *args, **kwargs) -> None:
        self.max_depth = max_depth
        Crawler.__init__(self, links, args, kwargs)

    def init_entrypoint(self) -> tuple:
        """
        Walk directory and extract root, dirs, files
        :return list: (root, dirs, files)
        """
        if os.path.islink(self.entrypoint):
            raise CrawlException("Link entrypoint is ignored!")
        try:
            return next(os.walk(self.entrypoint))
        except StopIteration:
            # If for any reason walk can't be finished raise an error
            raise CrawlException("Entrypoint could not be accessed!")

    def extract_hits(self) -> list:
        root, dirs, files = self.metadata
        return [os.path.join(root, filename) for filename in filter(self.is_hit, files)]

    def extract_links(self) -> list:
        root, dirs, files = self.metadata
        path_depth = self.entrypoint.count(os.sep)
        if path_depth < self.max_depth:
            return [os.path.join(root, path) for path in dirs]
        else:
            return []

    def is_hit(self, item: str) -> bool:
        return True

    def close_entrypoint(self) -> None:
        pass


class FileSearchCrawler(FileCrawler):

    def __init__(self, links: list, pattern: str = ".", max_depth: int = math.inf, *args, **kwargs) -> None:
        self.pattern = re.compile(pattern)
        FileCrawler.__init__(self, links, max_depth, args, kwargs)

    def is_hit(self, item: str) -> bool:
        return self.pattern.search(item) is not None
