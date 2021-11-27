from multiprocessing import Manager, Event, Process, Lock
from typing import Any, Optional

# Create global Process Manager
main_manager = Manager()


def worker_id_gen():
    worker_id = 0
    while True:
        yield worker_id
        worker_id += 1


class CrawlWorker(Process):
    id_gen = worker_id_gen()
    jobs_acquiring_lock = Lock()
    targets = main_manager.list()
    links_followed = main_manager.list()
    links_error = main_manager.list()

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
        # Crawl until wake_signal is high
        while self.wake_signal.wait():
            if crawler.links:
                # Crawl next link
                next(crawler)
                if self.sig_worker_idle.is_set() and len(crawler.links) > self.buffer_size:
                    # One of the workers is IDLE and Worker has more links than buffer size
                    with self.jobs_acquiring_lock:
                        # Keep links of buffer size
                        self.jobs_list += crawler.links[self.buffer_size:]
                        # Remove those links from crawler links
                        del crawler.links[self.buffer_size:]
            elif not self.jobs_list:
                # job_queue is empty
                # set wake_signal to low
                self.wake_signal.clear()
                # set worker_idle_signal to high
                self.sig_worker_idle.set()
                # Check if Worker should stop
                if self.stop_signal.is_set():
                    break
            else:
                # Crawler has no links to follow, but there are some links already in job_queue
                with self.jobs_acquiring_lock:
                    # Fill crawler.links from jobs_list of buffer_size
                    crawler.links += self.jobs_list[:self.buffer_size]
                    # Remove fetched links from jobs_list
                    del self.jobs_list[:self.buffer_size]
        # collect results and fill shared worker result lists
        self.targets += crawler.targets
        self.links_followed += crawler.links_followed
        self.links_error += crawler.links_error

    def stop(self) -> None:
        """
        Stop worker
        :return:
        """
        self.stop_signal.set()


class CrawlerManager:

    def __init__(self, crawler_class, links: list, num_proc: int = 4, *args: Any, **kwargs: Any) -> None:
        self.num_proc = num_proc
        self.crawler_class = crawler_class
        self.jobs_list = main_manager.list(links)
        self.sig_worker_idle = Event()
        self.jobs_acquiring_lock = Lock()
        self.args = args
        self.kwargs = kwargs
        self.workers = []

    def _init_workers(self) -> None:
        """
        Initiate workers
        Number of workers equals num_proc attribute value.
        :return: None
        """
        for i in range(self.num_proc):
            worker = CrawlWorker(self.crawler_class, self.sig_worker_idle, self.jobs_list,
                                 entrypoint=None, *self.args, **self.kwargs)
            self.workers.append(worker)
            worker.start()
            worker.wake_signal.set()

    def stop(self) -> None:
        """
        Stop all workers
        :return: None
        """
        for worker in self.workers:
            worker.stop()
            worker.wake_signal.set()

    def start(self) -> Optional[CrawlWorker]:
        """
        Start Manager ant it's Workers
        :return: CrawlWorker or None
        """
        # Spawn and start all workers
        self._init_workers()
        while self.sig_worker_idle.wait():
            # If one of the Workers is Idle
            # Count number of Idle workers
            idle_workers = 0
            for worker in self.workers:
                if not worker.wake_signal.is_set():
                    # Worker's wake_signal is low
                    # Wake up Worker
                    worker.wake_signal.set()
                    idle_workers += 1
            # Clear worker idle signal
            self.sig_worker_idle.clear()
            if idle_workers == self.num_proc and len(self.jobs_list) == 0:
                # All workers are idle and job_list is empty
                # All jobs are finished, close all workers
                self.stop()
                break

        worker = None
        for worker in self.workers:
            # Wait until all workers are finished
            worker.join()

        if worker is not None:
            # Return last worker which has reference to all results
            return worker
        else:
            return None
