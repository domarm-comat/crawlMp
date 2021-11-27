from abc import ABC, abstractmethod
from typing import Any


class Crawler(ABC):

    def __init__(self, entrypoint: Any, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.entrypoint = entrypoint
        self.metadata = ()
        self.targets = []
        self.links = [self.entrypoint]
        self.links_followed = []
        self.links_error = []

    def __iter__(self):
        return self

    def __next__(self):
        if len(self.links) > 0:
            try:
                next_link = self.links.pop(0)
                if next_link is not None:
                    self.crawl(next_link)
                    self.links_followed.append(next_link)
            except Exception:
                self.links_error.append(next_link)
            return self
        else:
            raise StopIteration

    @abstractmethod
    def init_entrypoint(self) -> tuple:
        ...

    @abstractmethod
    def extract_targets(self) -> list:
        ...

    @abstractmethod
    def extract_links(self) -> list:
        ...

    @abstractmethod
    def is_valid(self, item: Any) -> bool:
        ...

    @abstractmethod
    def close_entrypoint(self) -> None:
        ...

    def crawl(self, entrypoint: Any) -> None:
        if entrypoint is None:
            return
        self.entrypoint = entrypoint
        self.metadata = self.init_entrypoint()
        self.targets += self.extract_targets()
        self.links += self.extract_links()
        self.close_entrypoint()
