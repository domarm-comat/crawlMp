from abc import ABC, abstractmethod

from dataCrawler.backend.interfaces.target import Target


class Dumper(ABC):

    @abstractmethod
    def dump(self, target: Target):
        ...
