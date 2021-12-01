from multiprocessing import Event, Lock
from threading import Thread
from typing import Any, Optional, Callable

# Create global Process Manager
from crawlMp import share_manager
from crawlMp.sources.crawlWorker import CrawlWorker


class CrawlMp:

    def __init__(self, crawler_class, links: list, num_proc: int = 4, *args: Any, **kwargs: Any) -> None:
        assert num_proc > 0
        self.num_proc = num_proc
        self.crawler_class = crawler_class
        self.jobs_list = share_manager.list(links)
        self.sig_worker_idle = Event()
        self.jobs_acquiring_lock = Lock()
        self.args = args
        self.kwargs = kwargs
        self.workers = []
        self.running = False

    def _init_workers(self) -> None:
        """
        Initiate workers
        Number of workers equals num_proc attribute value.
        :return: None
        """
        # Reset results
        CrawlWorker.targets_found[:] = []
        CrawlWorker.links_followed[:] = []
        CrawlWorker.links_failed[:] = []

        for i in range(self.num_proc):
            worker = CrawlWorker(self.crawler_class, self.sig_worker_idle, self.jobs_list,
                                 links=None, *self.args, **self.kwargs)
            self.workers.append(worker)
            worker.start()
            worker.wake_signal.set()

    def stop_workers(self) -> None:
        """
        Stop all workers
        :return: None
        """
        for worker in self.workers:
            worker.stop()
            worker.wake_signal.set()

    def stop(self) -> None:
        self.running = False

    def _start(self, callback: Callable = None) -> Optional[CrawlWorker]:
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
                if not self.running or (idle_workers == self.num_proc and len(self.jobs_list) == 0):
                    # All workers are idle and job_list is empty
                    # All jobs are finished, close all workers
                    self.stop_workers()
                    break

        worker = None
        for worker in self.workers:
            # Wait until all workers are finished
            worker.join()

        output = worker.get_results()
        # Call the Callback if necessary
        if callback is not None:
            callback(output)
        else:
            return output

    def get_results(self):
        return self.workers[0].get_results()

    def start(self, callback: Callable = None) -> Optional[CrawlWorker]:
        """
        Start Manager ant it's Workers
        If callback is set, then start crawlers in the Thread and call callback in the end.
        :param callable callback: Callable
        :return: CrawlWorker or None
        """
        if callback is None:
            return self._start()
        else:
            assert callable(callback)
            Thread(target=self._start, args=(callback,)).start()
