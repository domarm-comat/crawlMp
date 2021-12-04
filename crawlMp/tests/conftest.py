import os.path

import pytest


@pytest.fixture(scope="session")
def fs_files_mock():
    path = "./crawlMp/tests/fs_files.txt"
    if not os.path.exists(path):
        path = "./fs_files.txt"
    with open(path) as fp:
        yield fp.readlines()


@pytest.fixture
def fake_fs(fs_files_mock, fs):
    p_size, p_name, p_type = fs_files_mock[0].strip().split("\t")
    ch_perm_to = []
    for mock_file in fs_files_mock:
        f_size, f_name, f_type = mock_file.strip().split("\t")
        try:
            if f_type in ("F", "FE"):
                fs.create_file(f_name)
            elif f_type in ("D", "DE"):
                fs.create_dir(f_name)
            elif f_type == "L":
                fs.create_symlink(f_name, p_name)
            if f_type[-1] == "E":
                ch_perm_to.append(f_name)
        except FileExistsError:
            pass
    for f_name in ch_perm_to:
        os.chown(f_name, 0, 0)
        os.chmod(f_name, 0o000)
    yield fs
