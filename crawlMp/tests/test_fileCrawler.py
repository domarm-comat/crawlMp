import math
from copy import copy

import pytest

from crawlMp.sources.fileCrawler import FileCrawler, FileSearchCrawler


@pytest.mark.parametrize("links", [["/"], ["/doc/source", "/numpy/doc"]], ids=["all", "two-dir"])
@pytest.mark.parametrize("max_depth", [0, 1, 2, math.inf], ids=["0", "1", "2", "all"])
@pytest.mark.parametrize("crawler_class", [FileCrawler, FileSearchCrawler], ids=["fc", "fcs"])
def test_fs_crawl(fake_fs, crawler_class, links, max_depth, request):
    test_id = request.node.callspec.id
    expected = {
        "fc-0-all": [38, 1, 0],
        "fc-0-two-dir": [11, 2, 0],
        "fc-1-all": [38, 1, 0],
        "fc-1-two-dir": [11, 2, 0],
        "fc-2-all": [550, 41, 1],
        "fc-2-two-dir": [11, 2, 0],
        "fc-all-all": [1811, 148, 2],
        "fc-all-two-dir": [387, 29, 1],
        "fcs-0-all": [38, 1, 0],
        "fcs-0-two-dir": [11, 2, 0],
        "fcs-1-all": [38, 1, 0],
        "fcs-1-two-dir": [11, 2, 0],
        "fcs-2-all": [550, 41, 1],
        "fcs-2-two-dir": [11, 2, 0],
        "fcs-all-all": [1811, 148, 2],
        "fcs-all-two-dir": [387, 29, 1],
    }

    crawl = None
    for crawl in crawler_class(copy(links), max_depth=max_depth):
        pass

    assert crawl is not None

    out = crawl.get_results()
    assert crawl.max_depth == max_depth
    assert len(out.targets_found) == expected[test_id][0]
    assert len(out.links_followed) == expected[test_id][1]
    assert len(out.links_failed) == expected[test_id][2]


@pytest.mark.parametrize("links", ["", "not_list", "/not/list"])
def test_fs_crawl_entrypoint_fail(fake_fs, links):
    with pytest.raises(AssertionError):
        FileCrawler(links)


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
