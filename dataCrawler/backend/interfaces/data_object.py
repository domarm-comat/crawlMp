from abc import ABC, abstractmethod


class Data_object(ABC):

    @abstractmethod
    def data(self):
        ...
