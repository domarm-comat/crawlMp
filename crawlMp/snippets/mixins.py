import os

from crawlMp import ActionException


class TargetDir:
    """
    Mixin class providing target_dir property.
    """
    _target_dir: str = "."

    @property
    def target_dir(self) -> str:
        return self._target_dir

    @target_dir.setter
    def target_dir(self, new_target_dir: str) -> None:
        if not os.path.isdir(new_target_dir):
            # Target dir does not exist, try to create it
            try:
                os.mkdir(new_target_dir)
            except OSError as e:
                raise ActionException(e)
        self._target_dir = new_target_dir
