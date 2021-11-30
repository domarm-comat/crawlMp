from threading import Event

import pytest

from crawlMp.sources.crawlMp import CrawlMp
from crawlMp.sources.fileCrawler import FileCrawler


@pytest.mark.parametrize("num_proc", [6, 8])
def test_crawlMp_num_proc(fake_fs, num_proc):
    manager = CrawlMp(FileCrawler, links=["/"], num_proc=num_proc)
    results = manager.start()
    assert True


def done_cb(results, done_event):
    done_event.set()


def test_crawlMp_callback(fake_fs):
    done_event = Event()
    manager = CrawlMp(FileCrawler, links=["/"])
    manager.start(callback=lambda results: done_cb(results, done_event))

    done_event.wait(timeout=5)
    assert True
