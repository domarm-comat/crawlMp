from multiprocessing import Lock, Event
from threading import Thread
from typing import Any, Callable

# Create global Process Manager
from crawlMp import share_manager
from crawlMp.sources.crawlWorker import CrawlWorker
from crawlMp.sources.results import Results


class CrawlMp:

    def __init__(self, crawler_class, links: list, num_proc: int = 4, buffer_size: int = 96, *args: Any,
                 **kwargs: Any) -> None:
        assert num_proc > 0
        self.num_proc = num_proc
        self.crawler_class = crawler_class
        self.jobs_list = share_manager.list(links)
        self.jobs_acquiring_lock = Lock()
        self.args = args
        self.kwargs = kwargs
        self.workers = []
        self.running = False
        self.buffer_size = buffer_size
        self.sig_resumed = Event()
        self.sig_paused = Event()
        self.sig_worker_idle = Event()
        self.results = Results(shared=True)

    def _init_workers(self) -> None:
        """
        Initiate workers
        Number of workers equals num_proc attribute value.
        :return: None
        """
        for i in range(self.num_proc):
            worker = CrawlWorker(self.results, self.crawler_class, self.jobs_list, self.sig_paused,
                                 self.sig_worker_idle, links=None, *self.args, **self.kwargs)
            self.workers.append(worker)
            worker.start()
            worker.wake_signal.set()

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
        if self.is_paused():
            self.resume()

    def _start_mp(self, callback: Callable = None) -> Results:
        """
        Start crawling using multiple workers.
        :param Callable callback: callback function
        :return Results: results
        """
        self.running = True
        # Spawn and start all workers
        self._init_workers()
        while True:
            idle_workers = 0
            try:
                self.sig_worker_idle.wait(timeout=1)
                # If one of the Workers is Idle
                # Count number of Idle workers
                for worker in self.workers:
                    if not worker.wake_signal.is_set():
                        # Worker's wake_signal is low
                        # Wake up Worker
                        worker.wake_signal.set()
                        idle_workers += 1
                # Clear worker idle signal
                self.sig_worker_idle.clear()
            except RuntimeError:
                continue
            finally:
                if self.is_paused():
                    self.sig_resumed.wait()
                elif not self.running or (idle_workers == self.num_proc and len(self.jobs_list) == 0):
                    # All workers are idle and job_list is empty
                    # All jobs are finished, close all workers
                    self.stop_workers()
                    break

        for worker in self.workers:
            # Wait until all workers are finished
            worker.join()
        # Call the Callback if necessary
        if callback is not None:
            callback(self.results)
        else:
            return self.results

    def _start_sp(self, callback: Callable = None) -> Results:
        """
        Start crawling in single process.
        Useful for small link sets when spawning processes would lead to overhead.
        :param Callable callback: callback function
        :return Results: results
        """
        self.running = True

        def flush_results(crawler) -> None:
            """
            Flush crawler results into shared worker results.
            :return: None
            """
            self.results.hits += crawler.results.hits
            self.results.links_followed += crawler.results.links_followed
            self.results.links_failed += crawler.results.links_failed
            crawler.results.reset()

        iterations = 0
        crawl = None
        for crawl in self.crawler_class(self.jobs_list[:], *self.args, **self.kwargs):
            if not self.running:
                break
            iterations += 1
            if iterations % self.buffer_size == 0:
                flush_results(crawl)

        if crawl is not None:
            # Flush rest of the results
            flush_results(crawl)

        # Call the Callback if necessary
        if callback is not None:
            callback(self.results)
        else:
            return self.results

    def append_links(self, links: list) -> None:
        """
        Add links, thread safe.
        :param list links: New links to crawl
        :return: None
        """
        self.jobs_list += links

    def start(self, callback: Callable = None, reset_results: bool = True) -> Results:
        """
        Start Manager and it's Workers
        If callback is set, then start crawlers in the Thread and call callback in the end.
        :param bool reset_results: Reset previous results
        :param callable callback: Callable
        :return: CrawlWorker or None
        """
        if reset_results:
            self.results.reset()
        start_method = self._start_mp if self.num_proc > 1 else self._start_sp

        if callback is None:
            return start_method()
        else:
            assert callable(callback)
            Thread(target=start_method, args=(callback,)).start()

    def pause(self) -> None:
        """
        Pause crawling until resume
        :return: None
        """
        self.sig_resumed.clear()
        self.sig_paused.set()

    def resume(self) -> None:
        """
        Resume crawling if paused
        :return: None
        """
        self.sig_paused.clear()
        self.sig_resumed.set()
        for worker in self.workers:
            worker.wake_signal.set()

    def is_paused(self) -> bool:
        """
        Check id crawling is paused.
        :return bool: pause status
        """
        return self.sig_paused.is_set()
