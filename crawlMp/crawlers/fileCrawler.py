import math
import os
import re
from builtins import OSError

from crawlMp import CrawlException
from crawlMp.constants import MODE_SIMPLE, MODE_EXTENDED
from crawlMp.crawlers.crawler import Crawler


class FileCrawler(Crawler):
    """
    Crawl through filesystem and find all files.
    Supporting two collection modes:
      - MODE_SIMPLE: ("Path")
      - MODE_EXTENDED: ("Path", "Size (b)", "Modified", "Accessed")
    MODE_EXTENDED is slower, because os.stat has to be called for every hit.
    """

    def __init__(self, links: list, max_depth: int = math.inf, mode: str = MODE_SIMPLE, *args, **kwargs) -> None:
        """
        Crawl is finished when links list is empty.
        :param list links: List of paths / entrypoints
        :param int max_depth: Maximum crawl depth (how deep crawler goes)
        :param str mode: Data collection mode
        :param args: other positional argument
        :param kwargs: other key arguments
        """
        assert max_depth >= 0
        self.max_depth = max_depth
        self.hits_header = {
            MODE_SIMPLE: ("Path",),
            MODE_EXTENDED: ("Path", "Size (b)", "Modified", "Accessed")
        }
        self.links_header = {
            MODE_SIMPLE: ("Path",),
            MODE_EXTENDED: ("Path",)
        }
        Crawler.__init__(self, links, mode, args, kwargs)

    def init_entrypoint(self) -> tuple:
        """
        Walk directory and extract root, dirs, files
        :return list: (root, dirs, files)
        """
        try:
            files, dirs = [], []
            for entry in os.scandir(self.entrypoint):
                if entry.is_file(follow_symlinks=False):
                    files.append((entry.name, entry.path))
                elif entry.is_dir(follow_symlinks=False):
                    dirs.append(entry.path)
                else:
                    # entry is not dir nor file, count it as a skipped link
                    self.results.links_skipped.append(entry.path)
            return dirs, files
        except (PermissionError, OSError):
            # Raise an error if for any reason scandir fails
            raise CrawlException("Entrypoint could not be accessed!")

    @staticmethod
    def crawl_modes() -> tuple:
        return MODE_SIMPLE, MODE_EXTENDED

    def extract_hits(self) -> list:
        """
        Extract all files in entrypoint
        Collect only filenames in SIMPLE_MODE
        Collect filenames, filesize, modification and access time
        :return list: list of files
        """
        _, files = self.metadata
        hits = []
        for filename, filepath in files:
            if self.is_hit(filename):
                if self.mode == MODE_SIMPLE:
                    hits.append(filepath, )
                elif self.mode == MODE_EXTENDED:
                    try:
                        file_stat = os.stat(filepath)
                        hits.append((filepath, file_stat.st_size, file_stat.st_mtime, file_stat.st_atime))
                    except FileNotFoundError:
                        # Ignore if File does not exist anymore
                        # this can happen for linux processes and such
                        continue
        return hits

    def extract_links(self) -> list:
        """
        Extract all other directories in entrypoint.
        :return list: list of directories
        """
        dirs, _ = self.metadata
        links = []
        for dir_path in dirs:
            if self.is_link(dir_path):
                links.append(dir_path)
        return links

    def is_hit(self, item: str) -> bool:
        """
        Just return True, since every item is already a file.
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
        return self.entrypoint.count(os.sep) < self.max_depth

    def close_entrypoint(self) -> None:
        """
        Just pass as we didn't allocate anything.
        :return: None
        """
        pass


class FileSearchCrawler(FileCrawler):
    """
    Crawl through filesystem and find all files matching regexp pattern.
    """

    def __init__(self, links: list, pattern: str = ".", max_depth: int = math.inf, mode=MODE_SIMPLE, *args,
                 **kwargs) -> None:
        """
        :param list links: List of paths / entrypoints
        :param str pattern: regular expression pattern used to search for hits
        :param int max_depth: Maximum crawl depth (how deep crawler goes)
        :param str mode: Data collection mode
        :param args: other positional argument
        :param kwargs: other key arguments
        """
        self.pattern = re.compile(pattern)
        FileCrawler.__init__(self, links, max_depth, mode, args, kwargs)

    def is_hit(self, item: str) -> bool:
        """
        Check if pattern was found in filepath
        :param str item: Filepath
        :return: True if pattern wqs found in string
        """
        return self.pattern.search(item) is not None
