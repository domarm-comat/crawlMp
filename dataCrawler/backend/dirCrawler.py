import math
import os

from dataCrawler import CrawlException
from dataCrawler.backend.interfaces.crawler import Crawler


class DirCrawler(Crawler):

    def __init__(self, entrypoint: str, max_depth: int = math.inf) -> None:
        self.max_depth = max_depth
        Crawler.__init__(self, entrypoint)

    def init_entrypoint(self) -> tuple:
        """
        Walk directory and extract root, dirs, files
        :return list: (root, dirs, files)
        """
        if not os.path.isdir(self.entrypoint):
            raise CrawlException("Entrypoint must be existing directory!")
        if os.path.islink(self.entrypoint):
            raise CrawlException("Link entrypoint is ignored!")
        return next(os.walk(self.entrypoint))

    def extract_targets(self) -> list:
        files = self.metadata[2]
        return list(filter(self.is_target, files))

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
