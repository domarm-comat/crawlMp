import math
from copy import copy
from typing import List, Type

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem

from crawlMp.crawlMp import CrawlMp
from crawlMp.crawlers.crawler import Crawler
from crawlMp.crawlers.crawler_fs import CrawlerFs, CrawlerSearchFs
from crawlMp.enums import Mode


@pytest.mark.parametrize("links", [["/"], ["/doc/source", "/numpy/doc"]], ids=["all", "two-dir"])
@pytest.mark.parametrize("max_depth", [0, 1, 2, math.inf], ids=["0", "1", "2", "all"])
@pytest.mark.parametrize("crawler_class", [CrawlerFs, CrawlerSearchFs], ids=["fc", "fcs"])
def test_fs_crawl(fake_fs: FakeFilesystem, crawler_class: Type[Crawler], links: List[str], max_depth: int,
                  request) -> None:
    test_id = request.node.callspec.id
    expected = {
        "fc-0-all": [38, 1, 0],
        "fc-0-two-dir": [11, 2, 1],
        "fc-1-all": [38, 1, 0],
        "fc-1-two-dir": [11, 2, 1],
        "fc-2-all": [550, 41, 2],
        "fc-2-two-dir": [11, 2, 1],
        "fc-all-all": [1811, 148, 2],
        "fc-all-two-dir": [387, 29, 1],
        "fcs-0-all": [38, 1, 0],
        "fcs-0-two-dir": [11, 2, 1],
        "fcs-1-all": [38, 1, 0],
        "fcs-1-two-dir": [11, 2, 1],
        "fcs-2-all": [550, 41, 2],
        "fcs-2-two-dir": [11, 2, 1],
        "fcs-all-all": [1811, 148, 2],
        "fcs-all-two-dir": [387, 29, 1],
    }

    manager = CrawlMp(CrawlerFs, links=copy(links), num_proc=1, max_depth=max_depth)
    manager.start()
    assert len(manager.results.hits) == expected[test_id][0]
    assert len(manager.results.links_followed) == expected[test_id][1]
    assert len(manager.results.links_skipped) == expected[test_id][2]


@pytest.mark.parametrize("links", ["", "not_list", "/not/list"])
def test_fs_crawl_entrypoint_fail(fake_fs, links) -> None:
    with pytest.raises(AssertionError):
        CrawlerFs(links)


@pytest.mark.parametrize("links", [["fail"], ["6"], ['/doc/source/af2py/', '/doc/csource/f2py/']])
def test_fs_crawl_faulty_entrypoint_fail(fake_fs: FakeFilesystem, links: List[str], request):
    test_id = request.node.callspec.id

    manager = CrawlMp(CrawlerFs, links=copy(links), num_proc=1)
    manager.start()

    assert len(manager.results.hits) == 0
    assert len(manager.results.links_followed) == 0
    if test_id == "links2":
        assert len(manager.results.links_skipped) == 2
    else:
        assert len(manager.results.links_skipped) == 1


@pytest.mark.parametrize("depth", [1, math.inf, 2, 3], ids=["d0", "d1", "d2", "d3"])
@pytest.mark.parametrize("pattern", ["\.py$", "\.svg$", "\.rst$", "\.build$|\.pyf$"], ids=["r0", "r1", "r2", "r3"])
def test_fs_crawl_search(fake_fs: FakeFilesystem, depth: int, pattern: str, request):
    test_id = request.node.callspec.id
    expected = {
        "r0-d0": (4, 1, 0),
        "r1-d0": (0, 1, 0),
        "r2-d0": (0, 1, 0),
        "r3-d0": (0, 1, 0),
        "r0-d1": (526, 148, 2),
        "r1-d1": (16, 148, 2),
        "r2-d1": (371, 148, 2),
        "r3-d1": (7, 148, 2),
        "r0-d2": (239, 41, 2),
        "r1-d2": (0, 41, 2),
        "r2-d2": (113, 41, 2),
        "r3-d2": (0, 41, 2),
        "r0-d3": (481, 81, 2),
        "r1-d3": (16, 81, 2),
        "r2-d3": (314, 81, 2),
        "r3-d3": (0, 81, 2),
    }
    manager = CrawlMp(CrawlerSearchFs, links=["/"], num_proc=1, pattern=pattern, max_depth=depth)
    manager.start()

    assert len(manager.results.hits) == expected[test_id][0]
    assert len(manager.results.links_followed) == expected[test_id][1]
    assert len(manager.results.links_skipped) == expected[test_id][2]


@pytest.mark.parametrize("num_proc", [1, 2])
def test_fs_crawl_extended_search(fake_fs: FakeFilesystem, num_proc: int) -> None:
    manager = CrawlMp(CrawlerSearchFs, links=["/"], num_proc=num_proc, pattern="\.py$", max_depth=2,
                      mode=Mode.EXTENDED)
    manager.start()
    df = manager.results.dataframe()
    assert len(manager.results.hits) == 239 == len(df)
    assert len(manager.results.links_followed) == 41
    assert len(manager.results.links_skipped) == 2


def test_fs_crawl_modes(fake_fs: FakeFilesystem) -> None:
    assert CrawlerFs.crawl_modes() == [Mode.SIMPLE, Mode.EXTENDED]
