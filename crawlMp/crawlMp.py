from multiprocessing import Lock, Event
from threading import Thread
from time import time
from typing import Any, Callable, Type

# Create global Process Manager
from crawlMp import share_manager, CrawlException
from crawlMp.crawlWorker import CrawlWorker
from crawlMp.crawlers.crawler import Crawler
from crawlMp.results import Results


class CrawlMp:
    """
    Crawl Manager, spawns workers that crawl through links.
    If keepalive is True, crawlMp keep Workers running and waiting for new links to crawl.
    One batch is finished, after all links were crawled.
    This is useful to manage multiple searches while in keepalive loop.
    """
    stopped = False
    batch_id = 0

    def __init__(self, crawler_class: Type[Crawler], links: list, keepalive=True, on_batch_done: Callable = None,
                 num_proc: int = 4, buffer_size: int = 96, actions: tuple = None, *args: Any, **kwargs: Any) -> None:
        """
        :param crawler_class: Crawler class to use with Worker
        :param list links: List of entrypoints
        :param bool keepalive: don't stop workers after crawl finishes
        :param callable on_batch_done: callback on finished batch
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
        self.keepalive = keepalive
        self.on_batch_done = on_batch_done
        self.jobs_acquiring_lock = Lock()
        self.args = args
        self.kwargs = kwargs
        self.workers = []
        self.running = False
        self.buffer_size = buffer_size
        self.sig_resumed = Event()
        self.sig_paused = Event()
        self.sig_worker_idle = Event()
        self.sig_batch_done = Event()
        self.lock_jobs_acq = Lock()
        self.actions = actions
        self.results = Results(shared=True)

    def _init_workers(self) -> None:
        """
        Initiate workers
        Number of workers equals num_proc attribute value.
        :return: None
        """
        for i in range(self.num_proc):
            worker = CrawlWorker(self.results, self.crawler_class, self.jobs_list, self.sig_paused,
                                 self.sig_worker_idle, self.lock_jobs_acq, actions=self.actions, links=None, *self.args,
                                 **self.kwargs)
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
        self.stopped = True
        if self.is_paused():
            self.sig_paused.clear()
            self.sig_resumed.set()

    def _start(self, callback: Callable = None) -> 'CrawlMp':
        """
        Start crawling using multiple workers.
        :param Callable callback: callback function
        :return Results: results
        """
        # Spawn and start all workers
        self._init_workers()
        while True:
            idle_workers = 0
            if not self.sig_worker_idle.wait(timeout=0.1) and self.stopped or not self.running:
                # All workers are idle and job_list is empty
                # All jobs are finished, close all workers
                self.running = False
                self.stop_workers()
                break
            # If one of the Workers is Idle
            # Count number of Idle workers
            if len(self.jobs_list) > 0:
                for worker in self.workers:
                    if not worker.wake_signal.is_set():
                        # Worker's wake_signal is low
                        # Wake up Worker
                        worker.wake_signal.set()
                # Clear worker idle signal
                self.sig_worker_idle.clear()
                continue

            for worker in self.workers:
                if not worker.wake_signal.is_set():
                    idle_workers += 1
            if self.is_paused():
                self.sig_resumed.wait()
            elif not self.sig_batch_done.is_set() and idle_workers == self.num_proc and len(self.jobs_list) == 0:
                # All jobs in the batch are finished
                self.sig_batch_done.set()
                self.batch_id += 1
                if self.on_batch_done is not None:
                    self.on_batch_done(self)
                if self.keepalive:
                    self.running = False
                    self.stop_workers()
                    break

        for worker in self.workers:
            # Wait until all workers are finished
            worker.join()

        self.results.done_time = time()
        # Call the Callback if it's set
        if callback is not None:
            callback(self)
        else:
            return self

    def _init_start(self) -> None:
        self.results.start_time = time()
        self.running = True
        self.stopped = False
        self.sig_resumed.clear()
        self.sig_paused.clear()
        self.sig_worker_idle.clear()

    def start(self, callback: Callable = None, reset_results: bool = True) -> None:
        """
        Start crawl managers.
        If callback is set, then start crawlers in the Thread and call callback in the end.
        :param bool reset_results: Reset previous results
        :param callable callback: Callable
        :return: None
        """
        if self.running:
            raise CrawlException("Crawling is already running.")

        self._init_start()
        if reset_results:
            self.results.reset()

        if callback is None:
            self._start()
        else:
            assert callable(callback)
            Thread(target=self._start, args=(callback,)).start()

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
        :return bool: pause state
        """
        return self.sig_paused.is_set()

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
        self.sig_batch_done.clear()
