from abc import ABC, abstractmethod


class Target(ABC):

    @abstractmethod
    def data(self):
        ...
