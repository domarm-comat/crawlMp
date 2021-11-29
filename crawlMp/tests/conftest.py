import pytest
import pyfakefs
from pyfakefs.fake_filesystem import is_root


@pytest.fixture(scope="session")
def fs_files_mock():
    with open("./fs_files.txt") as fp:
        yield fp.readlines()


@pytest.fixture
def fake_fs(fs_files_mock, fs):
    p_size, p_name, p_type = fs_files_mock[0].strip().split("\t")
    for mock_file in fs_files_mock:
        f_size, f_name, f_type = mock_file.strip().split("\t")
        try:
            if f_type == "F":
                fs.create_file(f_name)
            elif f_type == "L":
                fs.create_link(f_name, p_name)
        except FileExistsError:
            pass
    yield fs
