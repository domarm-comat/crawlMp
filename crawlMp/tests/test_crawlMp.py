import pytest

from crawlMp.sources.crawlMp import CrawlMp
from crawlMp.sources.fileCrawler import FileCrawler


@pytest.mark.parametrize("num_proc", [1, 2, 3, 4, 5, 6, 7, 8])
def test_crawlMp_num_proc(fake_fs, num_proc):
    manager = CrawlMp(FileCrawler, links=["/"], num_proc=num_proc)
    manager.start()
    assert True