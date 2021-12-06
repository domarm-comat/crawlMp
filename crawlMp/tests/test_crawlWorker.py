from multiprocessing import Event
from threading import Thread
from time import sleep

import pytest

from crawlMp.crawlWorker import CrawlWorker
from crawlMp.crawlers.fileCrawler import FileCrawler
from crawlMp.results import Results


@pytest.mark.parametrize('execution_number', range(5))
def test_crawl_worker(fake_fs, execution_number):
    sig_pause = Event()
    sig_idle = Event()
    results = Results()
    job_list = ["/"]
    worker_1 = CrawlWorker(results, FileCrawler, job_list, sig_pause, sig_idle, links=None, buffer_size=5)
    t1 = Thread(target=worker_1.run)
    t1.start()
    worker_1.wake_signal.set()
    sig_pause.set()
    sleep(1)
    sig_pause.clear()
    sleep(0.1)
    worker_1.wake_signal.set()
    sleep(0.2)
    sig_idle.set()
    sleep(0.2)
    sig_idle.clear()
    worker_1.wake_signal.set()
    if (len(job_list) > 0 and not worker_1.sig_idle.is_set()):
        while len(job_list) != 0 or not worker_1.sig_idle.is_set():
            worker_1.sig_idle.wait(timeout=10)
            worker_1.stop()
            worker_1.wake_signal.set()
    else:
        worker_1.stop()
        worker_1.wake_signal.set()
    t1.join()
    worker_2 = CrawlWorker(results, FileCrawler, job_list, sig_pause, sig_idle, links=None)
    assert worker_2.worker_id - worker_1.worker_id == 1
    assert len(results.hits) == 1811
    assert len(results.links_followed) == 148
    assert len(results.links_skipped) == 2
