import os

import pytest

from crawlMp import ActionException
from crawlMp.actions.action_fs import Copy, Move, Remove


@pytest.mark.parametrize("target_dir", ["/numpy/random/include/", "/not_existed"])
def test_fs_Copy(fake_fs, target_dir):
    target_file = os.path.join(target_dir, "refguide_check.py")
    assert not os.path.isfile(target_file)
    action = Copy(target_dir=target_dir)
    action.do("/tools/refguide_check.py")
    assert os.path.isfile(target_file)


def test_fs_Copy_twice(fake_fs):
    target_dir = "/numpy/random/include/"
    target_file = os.path.join(target_dir, "refguide_check.py")
    assert not os.path.isfile(target_file)
    action = Copy(target_dir=target_dir)
    action.do("/tools/refguide_check.py")
    action.do("/tools/refguide_check.py")
    assert os.path.isfile(target_file)


def test_fs_Copy_fail(fake_fs):
    target_file = "/tools/non_existing_file"
    action = Remove()
    with pytest.raises(ActionException):
        action.do(target_file)


def test_fs_Remove(fake_fs):
    target_file = "/tools/refguide_check.py"
    assert os.path.isfile(target_file)
    action = Remove()
    action.do(target_file)
    assert not os.path.isfile(target_file)


def test_fs_Remove_fail(fake_fs):
    target_file = "/tools/non_existing_file"
    action = Remove()
    with pytest.raises(ActionException):
        action.do(target_file)


@pytest.mark.parametrize("target_dir", ["/numpy/random/include/", "/not_existed"])
def test_fs_Move(fake_fs, target_dir):
    source_file = "/tools/refguide_check.py"
    assert os.path.isfile(source_file)
    target_file = os.path.join(target_dir, "refguide_check.py")
    assert not os.path.isfile(target_file)
    action = Move(target_dir=target_dir)
    action.do(source_file)
    assert not os.path.isfile(source_file)
