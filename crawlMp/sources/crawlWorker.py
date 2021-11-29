from multiprocessing import Event, Process, Lock
from typing import Any

# Create global Process Manager
from crawlMp import share_manager
from crawlMp.sources.results import Results


def worker_id_gen():
    worker_id = 0
    while True:
        yield worker_id
        worker_id += 1


class CrawlWorker(Process):
    id_gen = worker_id_gen()
    jobs_acquiring_lock = Lock()
    targets_found = share_manager.list()
    links_followed = share_manager.list()
    links_failed = share_manager.list()

    def __init__(self, crawler_class, sig_worker_idle: Event, jobs_list: list, buffer_size: int = 64, *args: Any,
                 **kwargs: Any) -> None:
        Process.__init__(self)
        self.worker_id = next(self.id_gen)
        self.stop_signal = Event()
        self.wake_signal = Event()
        self.buffer_size = buffer_size
        self.crawler_class = crawler_class
        self.sig_worker_idle = sig_worker_idle
        self.jobs_list = jobs_list
        self.args = args
        self.kwargs = kwargs

    def run(self) -> None:
        """
        Worker body
        Create Crawler object and crawl through.
        :return: None
        """
        # Initiate Crawler object for current Worker
        crawler = self.crawler_class(*self.args, **self.kwargs)

        def flush_results():
            self.targets_found += crawler.targets_found
            self.links_followed += crawler.links_followed
            self.links_failed += crawler.links_failed
            crawler.targets_found = []
            crawler.links_followed = []
            crawler.links_failed = []

        iterations = 0
        # Crawl until wake_signal is high
        while self.wake_signal.wait():
            if self.stop_signal.is_set():
                # Check if Worker should stop
                break
            elif crawler.links:
                # Crawl next link
                next(crawler)
                if self.sig_worker_idle.is_set() and len(crawler.links) > self.buffer_size:
                    # One of the workers is IDLE and Worker has more links than buffer size
                    with self.jobs_acquiring_lock:
                        # Keep links of buffer size
                        self.jobs_list += crawler.links[self.buffer_size:]
                        # Remove those links from crawler links
                        del crawler.links[self.buffer_size:]
                iterations += 1
                if iterations % self.buffer_size == 0:
                    flush_results()
            elif not self.jobs_list:
                # job_queue is empty
                # set wake_signal to low
                self.wake_signal.clear()
                # set worker_idle_signal to high
                self.sig_worker_idle.set()
            else:
                # Crawler has no links to follow, but there are some links already in job_queue
                with self.jobs_acquiring_lock:
                    # Fill crawler.links from jobs_list of buffer_size
                    crawler.links += self.jobs_list[:self.buffer_size]
                    # Remove fetched links from jobs_list
                    del self.jobs_list[:self.buffer_size]
        flush_results()

    def stop(self) -> None:
        """
        Stop worker
        :return:
        """
        self.stop_signal.set()

    def get_results(self):
        return Results(targets_found=self.targets_found,
                       links_followed=self.links_followed,
                       links_failed=self.links_failed)