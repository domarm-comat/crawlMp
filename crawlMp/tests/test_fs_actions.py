import os

import pytest

from crawlMp import ActionException
from crawlMp.actions.fs.copy import CopyAction
from crawlMp.actions.fs.move import MoveAction
from crawlMp.actions.fs.remove import RemoveAction

@pytest.mark.parametrize("target_dir", ["/numpy/random/include/", "/not_existed"])
def test_fs_CopyAction(fake_fs, target_dir):
    target_file = os.path.join(target_dir, "refguide_check.py")
    assert not os.path.isfile(target_file)
    action = CopyAction(target_dir=target_dir)
    action.do("/tools/refguide_check.py")
    assert os.path.isfile(target_file)


def test_fs_CopyAction_twice(fake_fs):
    target_dir = "/numpy/random/include/"
    target_file = os.path.join(target_dir, "refguide_check.py")
    assert not os.path.isfile(target_file)
    action = CopyAction(target_dir=target_dir)
    action.do("/tools/refguide_check.py")
    action.do("/tools/refguide_check.py")
    assert os.path.isfile(target_file)


def test_fs_CopyAction_fail(fake_fs):
    target_file = "/tools/non_existing_file"
    action = RemoveAction()
    with pytest.raises(ActionException):
        action.do(target_file)


def test_fs_RemoveAction(fake_fs):
    target_file = "/tools/refguide_check.py"
    assert os.path.isfile(target_file)
    action = RemoveAction()
    action.do(target_file)
    assert not os.path.isfile(target_file)


def test_fs_RemoveAction_fail(fake_fs):
    target_file = "/tools/non_existing_file"
    action = RemoveAction()
    with pytest.raises(ActionException):
        action.do(target_file)


@pytest.mark.parametrize("target_dir", ["/numpy/random/include/", "/not_existed"])
def test_fs_MoveAction(fake_fs, target_dir):
    source_file = "/tools/refguide_check.py"
    assert os.path.isfile(source_file)
    target_file = os.path.join(target_dir, "refguide_check.py")
    assert not os.path.isfile(target_file)
    action = MoveAction(target_dir=target_dir)
    action.do(source_file)
    assert not os.path.isfile(source_file)
