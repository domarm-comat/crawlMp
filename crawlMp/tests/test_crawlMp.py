from threading import Event
from time import sleep

import pytest

from crawlMp.crawlMp import CrawlMp
from crawlMp.crawlers.fileCrawler import FileCrawler


def done_cb(results, done_event):
    done_event.set()


@pytest.mark.parametrize("num_proc", [1, 2, 4, 6, 8])
def test_crawlMp_num_proc(fake_fs, num_proc):
    done_event = Event()
    manager = CrawlMp(FileCrawler, links=["/"], num_proc=num_proc)
    manager.start(callback=lambda results: done_cb(results, done_event))

    done_event.wait()
    assert done_event.is_set()

    assert len(manager.results.hits) == 1811
    assert len(manager.results.links_followed) == 148
    assert len(manager.results.links_failed) == 2


def test_crawlMp_callback(fake_fs):
    done_event = Event()
    manager = CrawlMp(FileCrawler, links=["/"])
    manager.start(callback=lambda results: done_cb(results, done_event))

    done_event.wait(timeout=5)
    assert done_event.is_set()

    assert len(manager.results.hits) == 1811
    assert len(manager.results.links_followed) == 148
    assert len(manager.results.links_failed) == 2


def test_crawlMp_stop(fake_fs):
    done_event = Event()
    manager = CrawlMp(FileCrawler, links=["/"] * 100, num_proc=1)
    manager.start(callback=lambda results: done_cb(results, done_event))

    sleep(0.5)
    manager.stop()

    done_event.wait(timeout=5)
    assert done_event.is_set()


@pytest.mark.parametrize("num_proc", [0, -1])
def test_crawlMp_numproc_fail(fake_fs, num_proc):
    with pytest.raises(AssertionError):
        CrawlMp(FileCrawler, links=["/"], num_proc=num_proc)


def test_crawlMp_append_link(fake_fs):
    done_event = Event()
    multiplier = 30
    manager = CrawlMp(FileCrawler, links=["/"] * multiplier)
    manager.start(callback=lambda results: done_cb(results, done_event))

    append_link_times = 5
    for i in range(append_link_times):
        manager.append_links(["/"])

    done_event.wait(timeout=15)
    assert done_event.is_set()

    assert len(manager.results.hits) == 1811 * (append_link_times + multiplier)
    assert len(manager.results.links_followed) == 148 * (append_link_times + multiplier)
    assert len(manager.results.links_failed) == 2 * (append_link_times + multiplier)

@pytest.mark.parametrize('execution_number', range(5))
@pytest.mark.parametrize("pause_offset", [0, 0.1, 0.5])
def test_crawlMp_pause_resume(fake_fs, pause_offset, execution_number):
    done_event = Event()
    multiplier = 30
    manager = CrawlMp(FileCrawler, links=["/"] * multiplier)
    manager.start(callback=lambda results: done_cb(results, done_event))

    sleep(pause_offset)
    manager.pause()
    sleep(pause_offset)
    manager.resume()
    sleep(pause_offset)
    manager.pause()
    sleep(pause_offset)
    manager.resume()

    done_event.wait(timeout=15)
    assert done_event.is_set()

    assert len(manager.results.hits) == 1811 * multiplier
    assert len(manager.results.links_followed) == 148 * multiplier
    assert len(manager.results.links_failed) == 2 * multiplier


@pytest.mark.parametrize('execution_number', range(5))
@pytest.mark.parametrize("pause_offset", [0, 0.1, 0.5])
def test_crawlMp_pause_resume_stop(fake_fs, pause_offset, execution_number):
    done_event = Event()
    manager = CrawlMp(FileCrawler, links=["/"] * 100)
    manager.start(callback=lambda results: done_cb(results, done_event))

    sleep(pause_offset)
    manager.pause()
    sleep(pause_offset)
    manager.resume()
    sleep(pause_offset)
    manager.pause()
    sleep(pause_offset)
    manager.stop()

    done_event.wait(timeout=0.1)
    assert done_event.is_set()
