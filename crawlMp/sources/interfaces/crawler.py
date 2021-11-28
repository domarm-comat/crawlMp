from abc import ABC, abstractmethod
from typing import Any

from crawlMp import CrawlException
from crawlMp.sources.results import Results


class Crawler(ABC):

    def __init__(self, links: list, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.metadata = ()
        self.targets_found = []
        self.entrypoint = None
        self.links_followed = []
        self.links_failed = []
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
            self.links_failed.append(next_link)
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
    def extract_targets(self) -> list:
        """
        Extract all targets from current entrypoint / resource.
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
    def is_target(self, item: Any) -> bool:
        """
        Decide if input item is target or not.
        This method must be reimplemented.
        :param Any item: Input item
        :return bool: True if item is Target
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

    def get_results(self) -> Results:
        """
        Get Crawler results
        :return Results: Results object
        """
        return Results(targets_found=self.targets_found,
                       links_followed=self.links_followed,
                       links_failed=self.links_failed)

    def crawl(self, entrypoint: Any) -> None:
        """
        Init entrypoint (next link), extract links and targets, close entrypoint.
        :param Any entrypoint: Address of entrypoint / resource
        :return: None
        """
        if entrypoint is None:
            return
        self.entrypoint = entrypoint
        self.links_followed.append(entrypoint)
        self.metadata = self.init_entrypoint()
        self.targets_found += self.extract_targets()
        self.links += self.extract_links()
        self.close_entrypoint()
