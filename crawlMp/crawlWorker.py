from multiprocessing import Event, Process, Lock
from typing import Any, Iterator, Type

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
    jobs_acquiring_lock = Lock()

    def __init__(self, results: Results, crawler_class: Type[Crawler], jobs_list: list, sig_pause: Event,
                 sig_idle: Event, buffer_size: int = 96, *args: Any, **kwargs: Any) -> None:
        """
        :param Result results: results object
        :param crawler_class: Crawler class
        :param list jobs_list: list of links
        :param Event sig_pause: Pause signal
        :param Event sig_idle: Idle signal
        :param int buffer_size: Size of links buffer
        :param args:
        :param kwargs:
        """
        assert buffer_size >= 1
        Process.__init__(self)
        self.worker_id = next(self.id_gen)
        self.results = results
        self.stop_signal = Event()
        self.wake_signal = Event()
        self.buffer_size = buffer_size
        self.crawler_class = crawler_class
        self.jobs_list = jobs_list
        self.sig_pause = sig_pause
        self.sig_idle = sig_idle
        self.args = args
        self.kwargs = kwargs

    def run(self) -> None:
        """
        Worker body
        Initiate Crawler and crawl through
        :return: None
        """
        # Initiate Crawler object for current Worker
        crawler = self.crawler_class(*self.args, **self.kwargs)
        if self.results.shared:
            self.results.hits_header[:] = crawler.results.hits_header
            self.results.links_header[:] = crawler.results.links_header
        else:
            self.results.hits_header = crawler.results.hits_header
            self.results.links_header = crawler.results.links_header

        def flush_results(crawler) -> None:
            """
            Flush crawler results into shared worker results.
            :return: None
            """
            self.results.hits += crawler.results.hits
            self.results.links_followed += crawler.results.links_followed
            self.results.links_skipped += crawler.results.links_skipped
            crawler.results.reset()

        iterations = 0
        # Crawl until wake_signal is high
        while self.wake_signal.wait():
            if self.stop_signal.is_set():
                # Check if Worker should stop
                break
            elif self.sig_pause.is_set():
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
                iterations += 1
                if iterations % self.buffer_size == 0:
                    flush_results(crawler)
            elif self.jobs_list:
                # Crawler has no links to follow, but there are some links already in job_queue
                # Fill crawler.links from jobs_list of buffer_size
                with self.jobs_acquiring_lock:
                    crawler.links += self.jobs_list[:self.buffer_size]
                    # Remove fetched links from jobs_list
                    del self.jobs_list[:self.buffer_size]
            else:
                # job_queue is empty
                # set wake_signal to low
                self.wake_signal.clear()
                # set worker_idle_signal to high
                self.sig_idle.set()

        flush_results(crawler)

    def stop(self) -> None:
        """
        Stop worker
        :return:
        """
        self.stop_signal.set()
