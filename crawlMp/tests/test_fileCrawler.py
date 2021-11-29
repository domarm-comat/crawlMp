import math
from copy import copy

import pytest

from crawlMp.sources.fileCrawler import FileCrawler


@pytest.mark.parametrize("links", [["/"], ["/doc/source", "/numpy/doc"]])
@pytest.mark.parametrize("max_depth", [0, 1, 2, math.inf])
def test_fs_crawl(fake_fs, links, max_depth):
    file_crawler = FileCrawler(copy(links), max_depth=max_depth)
    assert file_crawler.max_depth == max_depth
    results = None
    for results in file_crawler:
        pass

    assert results is not None
