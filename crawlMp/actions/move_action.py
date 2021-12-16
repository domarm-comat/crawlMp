from shutil import move

from crawlMp import ActionException
from crawlMp.actions.action import Action


class MoveAction(Action):

    def __init__(self, target_dir, *args, **kwargs):
        Action.__init__(self, *args, **kwargs)
        self.target_dir = target_dir

    def do(self, link: str) -> str:
        try:
            return move(link, self.target_dir)
        except PermissionError as exception:
            raise ActionException(exception)
