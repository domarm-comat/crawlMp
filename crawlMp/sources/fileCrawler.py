import math
import os
from re import Pattern

from crawlMp import CrawlException
from crawlMp.sources.interfaces.crawler import Crawler


class FileCrawler(Crawler):

    def __init__(self, links: list, max_depth: int = math.inf) -> None:
        self.max_depth = max_depth
        Crawler.__init__(self, links)

    def init_entrypoint(self) -> tuple:
        """
        Walk directory and extract root, dirs, files
        :return list: (root, dirs, files)
        """
        if not os.path.isdir(self.entrypoint):
            raise CrawlException("Entrypoint must be existing directory!")
        elif os.path.islink(self.entrypoint):
            raise CrawlException("Link entrypoint is ignored!")
        try:
            return next(os.walk(self.entrypoint))
        except StopIteration:
            raise CrawlException("Entrypoint could not be accessed!")

    def extract_targets(self) -> list:
        root, dirs, files = self.metadata
        return [os.path.join(root, filename) for filename in filter(self.is_target, files)]

    def extract_links(self) -> list:
        root, dirs, files = self.metadata
        path_depth = self.entrypoint.count(os.sep)
        if path_depth < self.max_depth:
            return [os.path.join(root, path) for path in dirs]
        else:
            return []

    def is_target(self, item: str) -> bool:
        return True

    def close_entrypoint(self) -> None:
        pass


class FileSearchCrawler(FileCrawler):

    def __init__(self, links: list, pattern: Pattern, max_depth: int = math.inf) -> None:
        self.pattern = pattern
        FileCrawler.__init__(self, links, max_depth)

    def is_target(self, item: str) -> bool:
        return self.pattern.search(item) is not None
