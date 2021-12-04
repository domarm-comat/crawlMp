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
    worker = CrawlWorker(results, FileCrawler, job_list, sig_pause, sig_idle, links=["/"], buffer_size=5)
    CrawlWorker(results, FileCrawler, job_list, sig_pause, sig_idle, links=["/"], buffer_size=5)
    Thread(target=worker.run).start()
    worker.wake_signal.set()
    sig_pause.set()
    sleep(1)
    sig_pause.clear()
    sleep(0.1)
    worker.wake_signal.set()
    sleep(0.2)
    sig_idle.set()
    sleep(0.2)
    sig_idle.clear()
    worker.wake_signal.set()
    sleep(1)
    worker.stop()
    worker.wake_signal.set()