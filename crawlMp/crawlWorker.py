from multiprocessing import Event, Process, Lock
from typing import Any, Iterator, Type, List

from crawlMp.crawlers.crawler import Crawler
from crawlMp.results import Results


def worker_id_gen() -> Iterator:
    """
    Simple worker ID generator.
    :return: int
    """
    worker_id = 0
    while True:
        yield worker_id
        worker_id += 1


class CrawlWorker(Process):
    """
    Worker process, which will run Crawler.
    """
    id_gen = worker_id_gen()

    def __init__(self, results: Results, crawler_class: Type[Crawler], jobs_list: List[Any], sig_pause: Event,
                 sig_idle: Event, lock_jobs_acq: Lock, buffer_size: int = 96, *args: Any, **kwargs: Any) -> None:
        """
        :param Result results: results object
        :param crawler_class: Crawler class
        :param list jobs_list: list of links
        :param Event sig_pause: Pause signal
        :param Event sig_idle: Idle signal
        :param Lock lock_jobs_acq: Lock for job acquisition
        :param int buffer_size: Size of links buffer
        :param args:
        :param kwargs:
        """
        super().__init__()
        self.worker_id = next(self.id_gen)
        self.results = results
        self.stop_signal = Event()
        self.wake_signal = Event()
        self.buffer_size = buffer_size
        self.crawler_class = crawler_class
        self.jobs_list = jobs_list
        self.sig_pause = sig_pause
        self.sig_idle = sig_idle
        self.lock_jobs_acq = lock_jobs_acq
        self.args = args
        self.kwargs = kwargs

    @property
    def buffer_size(self):
        return self._buffer_size

    @buffer_size.setter
    def buffer_size(self, new_buffer_size: int):
        assert new_buffer_size >= 1
        self._buffer_size = new_buffer_size

    def run(self) -> None:
        """
        Worker body
        Initiate Crawler and crawl through
        :return: None
        """
        crawler = self.crawler_class(*self.args, **self.kwargs)

        def flush_results(worker_crawler: Crawler) -> None:
            """
            Flush crawler results into shared worker results.
            :return: None
            """
            self.results.hits += worker_crawler.results.hits
            self.results.links_followed += worker_crawler.results.links_followed
            self.results.links_skipped += worker_crawler.results.links_skipped
            worker_crawler.results.reset()

        # Set worker as active
        self.wake_signal.set()
        # Crawl until wake_signal is high
        while True:
            if not self.wake_signal.wait(timeout=0.1) and self.stop_signal.is_set():
                break
            else:
                if self.sig_pause.is_set():
                    self.wake_signal.clear()
                    self.sig_idle.set()
                elif crawler.links:
                    # Crawl next link
                    next(crawler)
                    if self.sig_idle.is_set() and len(crawler.links) > self.buffer_size:
                        # One of the workers is IDLE and Worker has more links than buffer size
                        # Keep links of buffer size
                        self.jobs_list += crawler.links[self.buffer_size:]
                        # Remove those links from crawler links
                        del crawler.links[self.buffer_size:]
                elif self.jobs_list:
                    # Crawler has no links to follow, but there are some links already in job_queue
                    # Fill crawler.links from jobs_list of buffer_size
                    with self.lock_jobs_acq:
                        crawler.links += self.jobs_list[:self.buffer_size]
                        # Remove fetched links from jobs_list
                        del self.jobs_list[:self.buffer_size]
                else:
                    # job_queue is empty
                    flush_results(crawler)
                    # set wake_signal to low
                    self.wake_signal.clear()
                    # set worker_idle_signal to high
                    self.sig_idle.set()
        flush_results(crawler)

    def stop(self) -> None:
        """
        Stop worker
        :return: None
        """
        self.stop_signal.set()
