from threading import Event
from time import sleep

import pytest

from crawlMp.sources.crawlMp import CrawlMp
from crawlMp.sources.fileCrawler import FileCrawler


def done_cb(results, done_event):
    done_event.set()


@pytest.mark.parametrize("num_proc", [4, 6, 8])
def test_crawlMp_num_proc(fake_fs, num_proc):
    done_event = Event()
    manager = CrawlMp(FileCrawler, links=["/"], num_proc=num_proc)
    manager.start(callback=lambda results: done_cb(results, done_event))

    done_event.wait()
    assert done_event.is_set()

    results = manager.get_results()
    assert len(results.targets_found) == 1811
    assert len(results.links_followed) == 148
    assert len(results.links_failed) == 2


def test_crawlMp_callback(fake_fs):
    done_event = Event()
    manager = CrawlMp(FileCrawler, links=["/"])
    manager.start(callback=lambda results: done_cb(results, done_event))

    done_event.wait(timeout=5)
    assert done_event.is_set()

    results = manager.get_results()
    assert len(results.targets_found) == 1811
    assert len(results.links_followed) == 148
    assert len(results.links_failed) == 2


def test_crawlMp_stop(fake_fs):
    done_event = Event()
    manager = CrawlMp(FileCrawler, links=["/"] * 100, num_proc=1)
    manager.start(callback=lambda results: done_cb(results, done_event))

    sleep(0.5)
    manager.stop()

    done_event.wait(timeout=5)
    assert done_event.is_set()
