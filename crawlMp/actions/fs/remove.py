from os import remove

from crawlMp import ActionException
from crawlMp.actions.action import Action


class RemoveAction(Action):
    """
    Remove file or folder.
    """

    def __init__(self, *args, **kwargs) -> None:
        """
        :param args:
        :param kwargs:
        """
        Action.__init__(self, *args, **kwargs)

    def do(self, link: str) -> None:
        """
        Remove link and return None.
        :param str link: input link
        :return: None
        """
        try:
            remove(link)
            return None
        except PermissionError as exception:
            raise ActionException(exception)
        except FileNotFoundError as exception:
            raise ActionException(exception)
