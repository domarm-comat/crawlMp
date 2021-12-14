from multiprocessing import Lock, Event
from threading import Thread
from time import sleep
from typing import Any, Callable, Type

# Create global Process Manager
from crawlMp import share_manager, CrawlException
from crawlMp.crawlWorker import CrawlWorker
from crawlMp.crawlers.crawler import Crawler
from crawlMp.results import Results


class CrawlMp:
    """
    Crawl Manager, spawns workers that crawl through links.
    """
    force_stop = False
    batch_id = 0

    def __init__(self, crawler_class: Type[Crawler], links: list, keepalive=True, on_batch_done: Callable = None,
                 num_proc: int = 4, buffer_size: int = 96, *args: Any, **kwargs: Any) -> None:
        """
        :param crawler_class: Crawler class to use with Worker
        :param list links: List of entrypoints
        :param int num_proc: Number of processes
        :param int buffer_size: Size of links buffer
        :param args:
        :param kwargs:
        """
        assert num_proc > 0
        assert buffer_size >= 1
        self.num_proc = num_proc
        self.crawler_class = crawler_class
        self.jobs_list = share_manager.list(links)
        self.stop_on_done = keepalive
        self.on_jobs_done = on_batch_done
        self.jobs_acquiring_lock = Lock()
        self.args = args
        self.kwargs = kwargs
        self.workers = []
        self.running = False
        self.buffer_size = buffer_size
        self.sig_resumed = Event()
        self.sig_paused = Event()
        self.sig_worker_idle = Event()
        self.sig_jobs_done = Event()
        self.lock_jobs_acq = Lock()
        self.results = Results(shared=True)

    def _init_workers(self) -> None:
        """
        Initiate workers
        Number of workers equals num_proc attribute value.
        :return: None
        """
        for i in range(self.num_proc):
            worker = CrawlWorker(self.results, self.crawler_class, self.jobs_list, self.sig_paused,
                                 self.sig_worker_idle, self.lock_jobs_acq, links=None, *self.args, **self.kwargs)
            self.workers.append(worker)
            worker.start()

            if not self.running:
                return

    def stop_workers(self) -> None:
        """
        Stop all workers
        :return: None
        """
        for worker in self.workers:
            worker.stop()
            worker.wake_signal.set()

    def stop(self) -> None:
        """
        Stop crawling
        :return: None
        """
        self.running = False
        self.force_stop = True
        if self.is_paused():
            self.sig_paused.clear()
            self.sig_resumed.set()

    def _start_mp(self, callback: Callable = None) -> Results:
        """
        Start crawling using multiple workers.
        :param Callable callback: callback function
        :return Results: results
        """
        # Spawn and start all workers
        self._init_workers()
        while True:
            jobs_count = len(self.jobs_list)
            idle_workers = 0
            try:
                self.sig_worker_idle.wait(timeout=0.1)
                # If one of the Workers is Idle
                # Count number of Idle workers
                if jobs_count > 0:
                    for worker in self.workers:
                        if not worker.wake_signal.is_set():
                            # Worker's wake_signal is low
                            # Wake up Worker
                            worker.wake_signal.set()
                            idle_workers += 1
                    # Clear worker idle signal
                    self.sig_worker_idle.clear()
                else:
                    for worker in self.workers:
                        if not worker.wake_signal.is_set():
                            idle_workers += 1
            except RuntimeError:
                pass
            finally:
                if self.is_paused():
                    self.sig_resumed.wait()
                elif not self.sig_jobs_done.is_set() and idle_workers == self.num_proc and jobs_count == 0:
                    self.sig_jobs_done.set()
                    self.batch_id += 1
                    if self.on_jobs_done is not None:
                        self.on_jobs_done(self)
                    if self.stop_on_done:
                        self.running = False
                        self.stop_workers()
                        break
                elif self.force_stop or not self.running:
                    # All workers are idle and job_list is empty
                    # All jobs are finished, close all workers
                    self.running = False
                    self.stop_workers()
                    break

        for worker in self.workers:
            # Wait until all workers are finished
            worker.join()
        # Call the Callback if it's set
        if callback is not None:
            callback(self)
        else:
            return self

    def _start_sp(self, callback: Callable = None) -> Results:
        """
        Start crawling in single process.
        Useful for small link sets when spawning processes would lead to overhead.
        :param Callable callback: callback function
        :return Results: results
        """

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
        crawl = None
        while True:
            if len(self.jobs_list) > 0:
                for crawl in self.crawler_class(self.jobs_list, *self.args, **self.kwargs):
                    if not self.running:
                        break
                    elif self.sig_paused.is_set():
                        self.sig_resumed.wait()
                    iterations += 1
                    if iterations % self.buffer_size == 0:
                        flush_results(crawl)

                flush_results(crawl)
                self.sig_jobs_done.set()
                self.batch_id += 1
                if self.on_jobs_done is not None:
                    self.on_jobs_done(self)
            if not self.stop_on_done and not self.force_stop:
                sleep(0.1)
            else:
                break

        self.running = False

        # Call the Callback if it's set
        if callback is not None:
            callback(self)
        else:
            return self

    def append_links(self, links: list) -> None:
        """
        Add links, thread safe.
        :param list links: New links to crawl
        :return: None
        """
        if not self.running:
            raise CrawlException("Crawler is already finished.")
        self.jobs_list += links
        for worker in self.workers:
            # Wake up all workers again
            worker.wake_signal.set()
        self.sig_jobs_done.clear()

    def _init_start(self):
        self.running = True
        self.force_stop = False
        self.sig_resumed.clear()
        self.sig_paused.clear()
        self.sig_worker_idle.clear()

    def start(self, callback: Callable = None, reset_results: bool = True) -> Results:
        """
        Start crawl managers.
        If callback is set, then start crawlers in the Thread and call callback in the end.
        :param bool reset_results: Reset previous results
        :param callable callback: Callable
        :return: CrawlWorker or None
        """
        if self.running:
            raise CrawlException("Crawling is already running.")

        self._init_start()
        if reset_results:
            self.results.reset()
        start_method = self._start_mp if self.num_proc > 1 else self._start_sp

        if callback is None:
            return start_method()
        else:
            assert callable(callback)
            Thread(target=start_method, args=(callback,)).start()

            for worker in self.workers:
                # Block until all workers are idle
                worker.wake_signal.wait()

    def pause(self) -> None:
        """
        Pause crawling until resume
        :return: None
        """
        self.sig_resumed.clear()
        self.sig_paused.set()

        for worker in self.workers:
            # Block until all workers are idle
            worker.sig_idle.wait()

    def resume(self) -> None:
        """
        Resume crawling if paused
        :return: None
        """
        self.sig_paused.clear()
        self.sig_resumed.set()

        for worker in self.workers:
            # Wake up all workers again
            worker.wake_signal.set()

    def is_paused(self) -> bool:
        """
        Check id crawling is paused.
        :return bool: pause status
        """
        return self.sig_paused.is_set()
