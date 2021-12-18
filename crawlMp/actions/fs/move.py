from shutil import move
import os
from crawlMp import ActionException
from crawlMp.actions.action import Action


class MoveAction(Action):
    """
    Move file or folder.
    """

    def __init__(self, target_dir: str, *args, **kwargs) -> None:
        """
        :param str target_dir: target directory for a moved link
        :param args:
        :param kwargs:
        """
        Action.__init__(self, *args, **kwargs)
        self.target_dir = target_dir
        if not os.path.isdir(self.target_dir):
            # Target dir does not exist, try to create id
            try:
                os.mkdir(self.target_dir)
            except OSError as e:
                raise ActionException(e)

    def do(self, link: str) -> str:
        """
        Move input link and return path to moved link.
        :param str link: input link
        :return str: path to moved link
        """
        try:
            return move(link, self.target_dir)
        except PermissionError as exception:
            raise ActionException(exception)
