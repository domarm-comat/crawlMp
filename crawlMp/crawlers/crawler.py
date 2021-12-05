from abc import ABC, abstractmethod
from typing import Any

from crawlMp import CrawlException
from crawlMp.results import Results


class Crawler(ABC):
    """
    Basic Crawler interface.
    """

    def __init__(self, links: list = None, *args, **kwargs):
        """
        :param list links: list of entrypoints
        :param args:
        :param kwargs:
        """
        assert isinstance(links, list) or links is None
        self.args = args
        self.kwargs = kwargs
        self.metadata = ()
        self.entrypoint = None
        self.results = Results()
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
            self.results.links_failed.append(next_link)
        return self

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
