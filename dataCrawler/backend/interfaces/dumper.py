from abc import ABC, abstractmethod

from dataCrawler.backend.interfaces.data_object import Data_object


class Dumper(ABC):

    @abstractmethod
    def dump(self, data_object: Data_object):
        ...
