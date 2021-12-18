import os.path
from shutil import copy, SameFileError

from crawlMp import ActionException
from crawlMp.actions.action import Action


class CopyAction(Action):
    """
    Copy file or folder.
    """

    def __init__(self, target_dir: str, *args, **kwargs) -> None:
        """
        :param str target_dir: target directory for a copy
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
        Copy input link and return path to copied link.
        :param str link: input link
        :return str: path to copied link
        """
        try:
            return copy(link, self.target_dir)
        except SameFileError:
            return os.path.join(self.target_dir, os.path.basename(link))
        except FileNotFoundError as exception:
            raise ActionException(exception)
