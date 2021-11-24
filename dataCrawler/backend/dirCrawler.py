import math
import os

from dataCrawler import CrawlException
from dataCrawler.backend.interfaces.crawler import Crawler


class DirCrawler(Crawler):

    def __init__(self, entrypoint: str, max_depth: int = math.inf):
        self.max_depth = max_depth
        self.depth_offset = entrypoint.count(os.sep)
        Crawler.__init__(self, entrypoint)

    def init_entrypoint(self) -> tuple:
        if not os.path.isdir(self.entrypoint):
            raise CrawlException("Entrypoint must be existing directory!")
        if os.path.islink(self.entrypoint):
            raise CrawlException("Link entrypoint is ignored!")
        return True,

    def extract_targets(self) -> list:
        root, dirs, files = next(os.walk(self.entrypoint))
        return list(filter(self.is_valid, files))

    def extract_links(self) -> list:
        root, dirs, files = next(os.walk(self.entrypoint))
        path_depth = self.entrypoint.count(os.sep) - self.depth_offset
        if path_depth < self.max_depth:
            return [os.path.join(self.entrypoint, path) for path in dirs]
        else:
            return []

    def is_valid(self, item: str) -> bool:
        return True

    def close_entrypoint(self):
        ...
