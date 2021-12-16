import os.path
from shutil import copy, SameFileError

from crawlMp import ActionException
from crawlMp.actions.action import Action


class CopyAction(Action):

    def __init__(self, target_dir, *args, **kwargs):
        Action.__init__(self, *args, **kwargs)
        self.target_dir = target_dir

    def do(self, link: str) -> str:
        try:
            return copy(link, self.target_dir)
        except SameFileError:
            return os.path.join(self.target_dir, os.path.basename(link))
        except FileNotFoundError as exception:
            raise ActionException(exception)
