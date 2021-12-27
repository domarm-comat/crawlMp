from abc import ABC, abstractmethod
from multiprocessing.managers import ListProxy
from typing import Any, Tuple, List, Optional

from crawlMp import CrawlException, ActionException
from crawlMp.actions.action import Action
from crawlMp.enums import Mode, Header_ref
from crawlMp.results import Results


class Crawler(ABC):
    """
    Basic Crawler interface.
    """

    def __init__(self, links: Optional[List[Any]] = None, mode: Mode = Mode.SIMPLE,
                 actions: Optional[Tuple[Action, ...]] = None, *args, **kwargs):
        """
        :param list links: list of entrypoints
        :param str mode: Data collection mode
        :param args:
        :param kwargs:
        """
        # crawling mode must be in hits and links headers
        self.args = args
        self.kwargs = kwargs
        self.actions = actions
        self.mode = mode
        self.metadata: Tuple[Any, ...] = ()
        self.entrypoint: Any = None
        self.results = Results(self.hits_header(self.mode), self.links_header(self.mode))
        self.links = links

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

    @property
    def mode(self) -> Mode:
        return self._mode

    @mode.setter
    def mode(self, new_mode: Mode) -> None:
        assert new_mode in self.crawl_modes()
        self._mode = new_mode

    @property
    def links(self) -> List[Any]:
        return self._links

    @links.setter
    def links(self, new_links: Optional[List[Any]]):
        assert isinstance(new_links, (list, ListProxy)) or new_links is None
        self._links = new_links if new_links is not None else []

    @property
    def actions(self):
        return self._actions

    @actions.setter
    def actions(self, new_actions: Tuple[Action, ...]):
        self._actions = () if new_actions is None else new_actions
        for action in self._actions:
            assert isinstance(action, Action)

    @staticmethod
    @abstractmethod
    def crawl_modes() -> List[Mode]:
        """
        Get available crawl modes.
        :return tuple: (Mode1, Mode2, ...)
        """
        ...

    @staticmethod
    @abstractmethod
    def links_header(mode: Mode = Mode.SIMPLE) -> Tuple[Header_ref, ...]:
        """
        Get links header
        :param Mode mode: crawl mode
        :return tuple: (Name, Type, Unit)
        """
        ...

    @staticmethod
    @abstractmethod
    def hits_header(mode: Mode = Mode.SIMPLE) -> Tuple[Header_ref, ...]:
        """
        Get hits header
        :param Mode mode: crawl mode
        :return tuple: (Name, Type, Unit)
        """
        ...

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

    @abstractmethod
    def init_entrypoint(self) -> Tuple[Any, ...]:
        """
        Initialize entrypoint / resource
        Good example is opening new webpage, when entrypoint is url.
        :return tuple: Resource metadata
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

    @abstractmethod
    def extract_hits(self) -> List[Any]:
        """
        Extract all hits from current entrypoint / resource.
        This method must be reimplemented.
        :return:
        """
        ...

    @abstractmethod
    def extract_links(self) -> List[Any]:
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
