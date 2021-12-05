from multiprocessing import Event
from threading import Thread
from time import sleep

from crawlMp.crawlWorker import CrawlWorker
from crawlMp.crawlers.fileCrawler import FileCrawler
from crawlMp.results import Results


def test_crawl_worker(fake_fs):
    sig_pause = Event()
    sig_idle = Event()
    results = Results()
    job_list = ["/"]
    worker_1 = CrawlWorker(results, FileCrawler, job_list, sig_pause, sig_idle, links=["/"], buffer_size=5)
    worker_2 = CrawlWorker(results, FileCrawler, job_list, sig_pause, sig_idle, links=["/"], buffer_size=5)
    Thread(target=worker_2.run).start()
    worker_2.wake_signal.set()
    sig_pause.set()
    sleep(1)
    sig_pause.clear()
    sleep(0.1)
    worker_2.wake_signal.set()
    sleep(0.2)
    sig_idle.set()
    sleep(0.2)
    sig_idle.clear()
    worker_2.wake_signal.set()
    sleep(1)
    worker_2.stop()
    worker_2.wake_signal.set()

    worker_2.sig_idle.wait(timeout=1)
    assert worker_2.worker_id - worker_1.worker_id == 1
    assert len(results.hits) == 3617
    assert len(results.links_followed) == 295
    assert len(results.links_skipped) == 4
