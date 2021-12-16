from abc import ABC, abstractmethod


class Action(ABC):

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    @abstractmethod
    def do(self, link: str) -> str:
        ...
