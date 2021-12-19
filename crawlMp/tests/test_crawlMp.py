from threading import Event
from time import sleep

import pytest

from crawlMp import CrawlException
from crawlMp.crawlMp import CrawlMp
from crawlMp.crawlers.crawler_fs import CrawlerFs


def done_cb(_, done_event):
    done_event.set()


@pytest.mark.parametrize("num_proc", [1, 2, 3])
def test_crawlMp_num_proc(fake_fs, num_proc):
    done_event = Event()
    manager = CrawlMp(CrawlerFs, links=["/"], num_proc=num_proc)
    manager.start(callback=lambda m: done_cb(m, done_event))

    done_event.wait(timeout=60)
    assert done_event.is_set()

    assert len(manager.results.hits) == 1811
    assert len(manager.results.links_followed) == 148
    assert len(manager.results.links_skipped) == 2


def test_crawlMp_callback(fake_fs):
    done_event = Event()
    manager = CrawlMp(CrawlerFs, links=["/"])
    manager.start(callback=lambda results: done_cb(results, done_event))

    done_event.wait(timeout=60)
    assert done_event.is_set()

    assert len(manager.results.hits) == 1811
    assert len(manager.results.links_followed) == 148
    assert len(manager.results.links_skipped) == 2


def test_crawlMp_stop(fake_fs):
    done_event = Event()
    manager = CrawlMp(CrawlerFs, links=["/"] * 100, num_proc=1)
    manager.start(callback=lambda results: done_cb(results, done_event))

    sleep(0.5)
    manager.stop()

    done_event.wait(timeout=60)
    assert done_event.is_set()


@pytest.mark.parametrize("num_proc", [0, -1])
def test_crawlMp_numproc_fail(fake_fs, num_proc):
    with pytest.raises(AssertionError):
        CrawlMp(CrawlerFs, links=["/"], num_proc=num_proc)


@pytest.mark.parametrize("buff_size", [0, -1])
def test_crawlMp_buffer_size_fail(fake_fs, buff_size):
    with pytest.raises(AssertionError):
        CrawlMp(CrawlerFs, links=["/"], buffer_size=buff_size)


@pytest.mark.parametrize("num_proc", [1, 2])
def test_crawlMp_append_fail(fake_fs, num_proc):
    done_event = Event()
    manager = CrawlMp(CrawlerFs, links=["/"], num_proc=num_proc)
    manager.start(callback=lambda results: done_cb(results, done_event))
    sleep(2)
    with pytest.raises(CrawlException):
        manager.append_links(["/"])


def batch_done_cb(manager):
    if manager.batch_id == 2:
        manager.stop()


@pytest.mark.parametrize("num_proc", [1, 2])
def test_crawlMp_append_job_keep_alive(fake_fs, num_proc):
    done_event = Event()
    manager = CrawlMp(CrawlerFs, links=["/"], num_proc=num_proc, keepalive=False, on_batch_done=batch_done_cb)
    manager.start(callback=lambda results: done_cb(results, done_event))
    sleep(2)
    manager.append_links(["/"])

    done_event.wait(timeout=60)
    assert done_event.is_set()

    assert len(manager.results.hits) == 3622
    assert len(manager.results.links_followed) == 296
    assert len(manager.results.links_skipped) == 4


@pytest.mark.parametrize('factor', range(2, 10, 2))
@pytest.mark.parametrize("pause_offset", [0.3, 0.5])
@pytest.mark.parametrize("num_proc", [1, 2])
def test_crawlMp_pause_resume(fake_fs, pause_offset, factor, num_proc):
    done_event = Event()
    manager = CrawlMp(CrawlerFs, links=["/"] * factor, num_proc=num_proc)
    manager.start(callback=lambda results: done_cb(results, done_event))

    sleep(pause_offset)
    manager.pause()
    sleep(pause_offset)
    manager.resume()
    sleep(pause_offset)
    manager.pause()
    sleep(pause_offset)
    manager.resume()

    done_event.wait(timeout=60)
    assert done_event.is_set()

    assert len(manager.results.hits) == 1811 * factor
    assert len(manager.results.links_followed) == 148 * factor
    assert len(manager.results.links_skipped) == 2 * factor


@pytest.mark.parametrize('factor', range(2, 10, 2))
@pytest.mark.parametrize("pause_offset", [0.1, 0.5])
@pytest.mark.parametrize("num_proc", [1, 2])
def test_crawlMp_pause_resume_stop(fake_fs, factor, pause_offset, num_proc):
    done_event = Event()
    manager = CrawlMp(CrawlerFs, links=["/"] * factor, num_proc=num_proc)
    manager.start(callback=lambda results: done_cb(results, done_event))

    sleep(pause_offset)
    manager.pause()
    sleep(pause_offset)
    manager.resume()
    sleep(pause_offset)
    manager.pause()
    sleep(pause_offset)
    manager.stop()
    done_event.wait(timeout=5)
    assert done_event.is_set()
