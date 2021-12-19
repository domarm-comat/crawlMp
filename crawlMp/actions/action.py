from abc import ABC, abstractmethod
from typing import Any


class Action(ABC):
    """
    Action interface.
    Each  action should do only one main function.
    Method "do" must return link, which will be used in following action.
    Example of action chain:
    Crawl and search for .jpg files -> Action fs Copy -> Action Image Resize on copied .jpg file
    """

    def __init__(self, *args, **kwargs) -> None:
        self.args = args
        self.kwargs = kwargs

    @abstractmethod
    def do(self, link: Any) -> Any:
        """
        Main body of action.
        If ActionException is raised, link won't be count as a hit.
        :param Any link: input link
        :return Any: link
        """
        ...
