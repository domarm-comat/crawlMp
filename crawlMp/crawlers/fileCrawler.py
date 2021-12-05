import math
import os
import re

from crawlMp import CrawlException
from crawlMp.crawlers.crawler import Crawler


class FileCrawler(Crawler):
    """
    Crawl through filesystem and find all files.
    """

    def __init__(self, links: list, max_depth: int = math.inf, *args, **kwargs) -> None:
        """
        Crawl is finished when links list is empty.
        :param list links: List of paths / entrypoints
        :param int max_depth: Maximum crawl depth (how deep crawler goes)
        :param args: other positional argument
        :param kwargs: other key arguments
        """
        assert max_depth >= 0
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
        """
        Extract all files in entrypoint
        :return list: list of files
        """
        root, dirs, files = self.metadata
        hits = []
        for filename in files:
            # if root == os.sep:
            #     filepath = root + filename
            # else:
            #     filepath = root + os.sep + filename
            filepath = os.path.join(root, filename)
            if self.is_hit(filepath):
                hits.append(filepath)
        return hits

    def extract_links(self) -> list:
        """
        Extract all other directories in entrypoint.
        :return list: list of directories
        """
        root, dirs, files = self.metadata
        links = []
        for dirname in dirs:
            # if root == os.sep:
            #     dirpath = root + dirname
            # else:
            #     dirpath = root + os.sep + dirname
            dirpath = os.path.join(root, dirname)
            if self.is_link(dirpath):
                links.append(dirpath)
        return links

    def is_hit(self, item: str) -> bool:
        """
        Just return True, since very item is already file.
        :param str item: Filepath
        :return bool: True
        """
        return True

    def is_link(self, item: str) -> bool:
        """
        Check if depth is < than max_depth.
        :param str item: Directory
        :return bool: True if path_depth < self.max_depth
        """
        path_depth = self.entrypoint.count(os.sep)
        return path_depth < self.max_depth

    def close_entrypoint(self) -> None:
        """
        Just pass as we didn't allocate anything.
        :return: None
        """
        pass


class FileSearchCrawler(FileCrawler):
    """
    Crawl through filesystem and find all files by regexp pattern.
    """

    def __init__(self, links: list, pattern: str = ".", max_depth: int = math.inf, *args, **kwargs) -> None:
        self.pattern = re.compile(pattern)
        FileCrawler.__init__(self, links, max_depth, args, kwargs)

    def is_hit(self, item: str) -> bool:
        """
        Check if pattern was found in filepath
        :param str item: Filepath
        :return: True if pattern wqs found in string
        """
        return self.pattern.search(item) is not None
