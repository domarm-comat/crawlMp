from abc import ABC, abstractmethod
from multiprocessing.managers import ListProxy
from typing import Any

from crawlMp import CrawlException, ActionException
from crawlMp.constants import MODE_SIMPLE
from crawlMp.results import Results


class Crawler(ABC):
    """
    Basic Crawler interface.
    """
    hits_header = None
    links_header = None

    def __init__(self, links: list = None, mode: str = MODE_SIMPLE, actions: tuple = None, *args, **kwargs):
        """
        :param list links: list of entrypoints
        :param str mode: Data collection mode
        :param args:
        :param kwargs:
        """
        assert isinstance(links, (list, ListProxy)) or links is None
        # headers for hits and links must be defined
        assert self.hits_header is not None
        assert self.links_header is not None
        # crawling mode must be in hits and links headers
        assert mode in self.hits_header
        assert mode in self.links_header
        self.actions = () if actions is None else actions
        self.mode = mode
        self.args = args
        self.kwargs = kwargs
        self.metadata = ()
        self.entrypoint = None
        self.results = Results()
        self.results.hits_header = self.hits_header[self.mode]
        self.results.links_header = self.links_header[self.mode]
        self.links = links if links is not None else []

    def __iter__(self):
        return self

    def __next__(self):
        """
        Generate next link and execute crawl method over it.
        :return Crawler: self object
        """
        try:
            next_link = self.links.pop(0)
        except IndexError:
            # No other links exists, stop iteration
            raise StopIteration
        try:
            self.crawl(next_link)
        except CrawlException:
            # If crawl fails for any reason, don't follow that link
            self.results.links_skipped.append(next_link)
        return self

    def execute_actions(self, hit: Any) -> bool:
        """
        Execute all actions sequence on the given hit.
        Actions are organized in a pipeline, feeding output of one action to the next action.
        Return True if whole pipeline was successfully executed.
        :param Any hit: input hit
        :return:
        """
        for action in self.actions:
            try:
                hit = action.do(hit)
            except ActionException:
                return False
        return True

    @abstractmethod
    def init_entrypoint(self) -> tuple:
        """
        Initialize entrypoint / resource
        Good example is opening new webpage, when entrypoint is url.
        :return tuple: Resource metadata
        """
        ...

    @abstractmethod
    def extract_hits(self) -> list:
        """
        Extract all hits from current entrypoint / resource.
        This method must be reimplemented.
        :return:
        """
        ...

    @abstractmethod
    def extract_links(self) -> list:
        """
        Extract all links from current entrypoint / resource.
        This method must be reimplemented.
        :return list: list of extracted links
        """
        ...

    @abstractmethod
    def is_hit(self, item: Any) -> bool:
        """
        Decide if input item is hits or not.
        This method must be reimplemented.
        :param Any item: Input item
        :return bool: True if item is a Hit
        """
        ...

    @abstractmethod
    def is_link(self, item: Any) -> bool:
        """
        Decide if input item is link or not.
        This method must be reimplemented.
        :param Any item: Input item
        :return bool: True if item is a Link
        """
        ...

    @abstractmethod
    def close_entrypoint(self) -> None:
        """
        Clean allocated resources attached to entrypoint / resource.
        This method must be reimplemented.
        :return: None
        """
        ...

    @staticmethod
    @abstractmethod
    def crawl_modes() -> tuple:
        """
        Get available crawl modes.
        :return tuple: (Mode1, Mode2, ...)
        """
        ...

    def crawl(self, entrypoint: Any) -> None:
        """
        Init entrypoint (next link), extract links and hits, close entrypoint.
        :param Any entrypoint: Address of entrypoint / resource
        :return: None
        """
        if entrypoint is None:
            return
        self.entrypoint = entrypoint
        self.metadata = self.init_entrypoint()
        self.results.links_followed.append(entrypoint)
        self.results.hits += self.extract_hits()
        self.links += self.extract_links()
        self.close_entrypoint()
