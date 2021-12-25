import os
import re
from builtins import OSError
from typing import Tuple, List, Optional, Any

from crawlMp import CrawlException
from crawlMp.actions.action import Action
from crawlMp.constants import inf_int
from crawlMp.crawlers.crawler import Crawler
from crawlMp.enums import Mode, Header, Header_ref


class CrawlerFs(Crawler):
    """
    Crawl through filesystem and find all files.
    Supporting two collection modes:
      - MODE_SIMPLE: (PATH)
      - MODE_EXTENDED: (PATH, SIZE, MODIFIED, ACCESSED)
    MODE_EXTENDED is slower, because os.stat has to be called for every hit.
    """

    def __init__(self, links: List[str], max_depth: int = inf_int, mode: Mode = Mode.SIMPLE,
                 actions: Optional[Tuple[Action, ...]] = None, *args, **kwargs) -> None:
        """
        Crawl is finished when links list is empty.
        :param list links: List of paths / entrypoints
        :param int max_depth: Maximum crawl depth (how deep crawler goes)
        :param str mode: Data collection mode
        :param args: other positional argument
        :param kwargs: other key arguments
        """
        assert max_depth >= 0
        self.actions = actions
        self.max_depth = max_depth
        Crawler.__init__(self, links, mode, actions, args, kwargs)

    def init_entrypoint(self) -> Tuple[List, List]:
        """
        Walk directory and extract list of dirs, files
        :return tuple: ([dirs], [files])
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
            raise CrawlException("Entrypoint cannot be accessed!")

    @staticmethod
    def links_header(mode: Mode = Mode.SIMPLE) -> Tuple[Header_ref, ...]:
        if mode == Mode.EXTENDED:
            return (Header.PATH, str, None),
        return (Header.PATH, str, None),

    @staticmethod
    def hits_header(mode: Mode = Mode.SIMPLE) -> Tuple[Header_ref, ...]:
        if mode == Mode.EXTENDED:
            return ((Header.PATH, str, None),
                    (Header.NAME, str, None),
                    (Header.SIZE, float, "byte"),
                    (Header.MODIFIED, float, "timestamp"),
                    (Header.ACCESSED, float, "timestamp"))

        return ((Header.PATH, str, None),
                (Header.NAME, str, None))

    @staticmethod
    def crawl_modes() -> List[Mode]:
        return [Mode.SIMPLE, Mode.EXTENDED]

    def extract_hits(self) -> List[Tuple[Any, ...]]:
        """
        Extract all files in entrypoint
        Collect only filenames in SIMPLE_MODE
        Collect filenames, filesize, modification and access time
        :return list: list of files
        """
        _, files = self.metadata
        hits: List[Tuple[Any, ...]] = []
        for filename, filepath in files:
            if self.is_hit(filename):
                if not self.execute_actions(filepath):
                    # Skip hit, if not all actions were successful
                    continue
                if self.mode == Mode.SIMPLE:
                    hits.append((filepath, filename))
                elif self.mode == Mode.EXTENDED:
                    try:
                        file_stat = os.stat(filepath)
                        hits.append((filepath, filename, file_stat.st_size, file_stat.st_mtime, file_stat.st_atime))
                    except FileNotFoundError:
                        # Ignore if File does not exist anymore
                        # this can happen for linux processes and such
                        continue
        return hits

    def extract_links(self) -> List[Tuple]:
        """
        Extract all other directories in entrypoint.
        :return list: list of directories
        """
        dirs, _ = self.metadata
        links = []
        for dir_path in dirs:
            if self.is_link(dir_path):
                links.append(dir_path, )
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
        Just pass, as we didn't allocate any resources.
        :return: None
        """
        pass


class CrawlerSearchFs(CrawlerFs):
    """
    Crawl through filesystem and find all files matching regexp pattern.
    """

    def __init__(self, links: List[str], pattern: str = ".", max_depth: int = inf_int, mode=Mode.SIMPLE,
                 actions: Optional[Tuple[Action, ...]] = None, *args, **kwargs) -> None:
        """
        :param list links: List of paths / entrypoints
        :param str pattern: regular expression pattern used to search for hits
        :param int max_depth: Maximum crawl depth (how deep crawler goes)
        :param str mode: Data collection mode
        :param args: other positional argument
        :param kwargs: other key arguments
        """
        self.pattern = re.compile(pattern)
        CrawlerFs.__init__(self, links, max_depth, mode, actions, args, kwargs)

    def is_hit(self, item: str) -> bool:
        """
        Check if pattern was found in filepath
        :param str item: Filepath
        :return: True if pattern wqs found in string
        """
        return self.pattern.search(item) is not None
