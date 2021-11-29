import pytest


@pytest.fixture(scope="session")
def fs_files_mock():
    with open("./fs_files.txt") as fp:
        yield fp.readlines()


@pytest.fixture
def fake_fs(fs_files_mock, fs):
    for mock_file in fs_files_mock:
        f_size, f_name = mock_file.strip().split("\t")
        try:
            fs.create_file(f_name)
        except FileExistsError:
            pass
    yield fs
