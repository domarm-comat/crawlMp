import os.path
from os import remove
from shutil import copy, SameFileError, move

from crawlMp import ActionException
from crawlMp.actions.action import Action


class Copy(Action):
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
            # Target dir does not exist, try to create it
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
            # File already exists, this is valid outcome, so just return new path.
            return os.path.join(self.target_dir, os.path.basename(link))
        except FileNotFoundError as exception:
            raise ActionException(exception)


class Move(Action):
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
            # Target dir does not exist, try to create it
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


class Remove(Action):
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
