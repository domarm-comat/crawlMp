import math
from copy import copy

import pytest

from crawlMp.sources.fileCrawler import FileCrawler


@pytest.mark.parametrize("links", [["/"], ["/doc/source", "/numpy/doc"]], ids=["all", "two-dir"])
@pytest.mark.parametrize("max_depth", [0, 1, 2, math.inf], ids=["0", "1", "2", "all"])
def test_fs_crawl(fake_fs, links, max_depth, request):
    test_id = request.node.callspec.id
    expected = {
        "0-all": [36, 1, 0],
        "0-two-dir": [11, 2, 0],
        "1-all": [36, 1, 0],
        "1-two-dir": [11, 2, 0],
        "2-all": [546, 41, 0],
        "2-two-dir": [11, 2, 0],
        "all-all": [1816, 147, 0],
        "all-two-dir": [386, 28, 0],
    }

    crawl = None
    for crawl in FileCrawler(copy(links), max_depth=max_depth):
        pass

    assert crawl is not None

    out = crawl.get_results()
    assert crawl.max_depth == max_depth
    assert len(out.targets_found) == expected[test_id][0]
    assert len(out.links_followed) == expected[test_id][1]
    assert len(out.links_failed) == expected[test_id][2]


def test_fs_crawl_empty_entrypoint_fail(fake_fs):
    with pytest.raises(AssertionError):
        FileCrawler("")


@pytest.mark.parametrize("links", [["fail"], ["6"], ['/doc/source/af2py/', '/doc/csource/f2py/']])
def test_fs_crawl_faulty_entrypoint_fail(fake_fs, links, request):
    test_id = request.node.callspec.id
    crawl = None
    for crawl in FileCrawler(copy(links)):
        pass

    assert crawl is not None

    out = crawl.get_results()
    assert len(out.targets_found) == 0
    assert len(out.links_followed) == 0
    if test_id == "links2":
        assert len(out.links_failed) == 2
    else:
        assert len(out.links_failed) == 1
