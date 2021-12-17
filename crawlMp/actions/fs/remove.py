from os import remove

from crawlMp import ActionException
from crawlMp.actions.action import Action


class RemoveAction(Action):

    def __init__(self, *args, **kwargs):
        Action.__init__(self, *args, **kwargs)

    def do(self, link: str) -> str:
        try:
            remove(link)
            return link
        except PermissionError as exception:
            raise ActionException(exception)
        except FileNotFoundError as exception:
            raise ActionException(exception)
