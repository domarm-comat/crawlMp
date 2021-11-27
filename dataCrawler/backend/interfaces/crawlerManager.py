from multiprocessing import Manager, Event, Process, Lock


def id_gen():
    id = 0
    while True:
        yield id
        id += 1


class CrawlWorker(Process):
    id_gen = id_gen()
    jobs_acquiring_lock = Lock()

    def __init__(self, crawler_class, sig_worker_idle, jobs_queue, buffer_size=64, *args, **kwargs):
        Process.__init__(self)
        self.worker_id = next(self.id_gen)
        self.stop_signal = Event()
        self.wake_signal = Event()
        self.buffer_size = buffer_size
        self.crawler_class = crawler_class
        self.sig_worker_idle = sig_worker_idle
        self.jobs_queue = jobs_queue
        self.args = args
        self.kwargs = kwargs

    def run(self) -> None:
        # print(f"Worker {self.worker_id} start")
        crawler = self.crawler_class(*self.args, **self.kwargs)
        while self.wake_signal.wait():
            if crawler.links:
                next(crawler)
                if self.sig_worker_idle.is_set() and len(crawler.links) > self.buffer_size:
                    self.jobs_queue += crawler.links[self.buffer_size:]
                    del crawler.links[self.buffer_size:]
            elif not self.jobs_queue:
                self.wake_signal.clear()
                self.sig_worker_idle.set()
                if self.stop_signal.is_set():
                    break
            else:
                with self.jobs_acquiring_lock:
                    crawler.links += self.jobs_queue[:self.buffer_size]
                    del self.jobs_queue[:self.buffer_size]

        # print(len(crawler.targets))
        # print(f"Worker {self.worker_id} quit")

    def stop(self):
        self.stop_signal.set()


class CrawlerManager:

    def __init__(self, crawler_class, links, num_proc=4, *args, **kwargs):
        self.manager = Manager()
        self.num_proc = num_proc
        self.crawler_class = crawler_class
        self.jobs_queue = self.manager.list(links)
        self.sig_worker_idle = Event()
        self.jobs_acquiring_lock = Lock()
        self.args = args
        self.kwargs = kwargs
        self.workers = []

    def _init_workers(self):
        for i in range(self.num_proc):
            try:
                entrypoint = self.jobs_queue.pop(0)
            except IndexError:
                entrypoint = None
            worker = CrawlWorker(self.crawler_class, self.sig_worker_idle, self.jobs_queue,
                                 entrypoint=entrypoint, *self.args, **self.kwargs)
            self.workers.append(worker)
            worker.start()
            worker.wake_signal.set()

    def stop(self):
        for worker in self.workers:
            worker.stop()
            worker.wake_signal.set()

    def start(self):
        self._init_workers()
        while self.sig_worker_idle.wait():
            idle_workers = 0
            for worker in self.workers:
                if not worker.wake_signal.is_set():
                    worker.wake_signal.set()
                    idle_workers += 1
            self.sig_worker_idle.clear()
            if idle_workers == self.num_proc and len(self.jobs_queue) == 0:
                self.stop()
                break

        for worker in self.workers:
            worker.join()

        print("All done!")
