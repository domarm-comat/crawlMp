from abc import ABC, abstractmethod
from time import sleep
from typing import Any


class Crawler(ABC):

    def __init__(self, entrypoint: Any, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.entrypoint = entrypoint
        self.metadata = ()
        self.targets = []
        self.links = [self.entrypoint]
        self.links_followed = []
        self.links_error = []

    def __iter__(self):
        return self

    def __next__(self):
        if len(self.links) > 0:
            try:
                next_link = self.links.pop(0)
                self.crawl(next_link)
                self.links_followed.append(next_link)
            except Exception as e:
                self.links_error.append(next_link)
                # print(f"Exception entering {self.entrypoint}, ERROR: {e}")
            return self
        else:
            raise StopIteration

    @abstractmethod
    def init_entrypoint(self) -> tuple:
        ...

    @abstractmethod
    def extract_targets(self) -> list:
        ...

    @abstractmethod
    def extract_links(self) -> list:
        ...

    @abstractmethod
    def is_valid(self, item: Any) -> bool:
        ...

    @abstractmethod
    def close_entrypoint(self):
        ...

    def crawl(self, entrypoint: Any):
        if entrypoint is None:
            return
        self.entrypoint = entrypoint
        self.metadata = self.init_entrypoint()
        self.targets += self.extract_targets()
        self.links += self.extract_links()
        self.close_entrypoint()


# from multiprocessing import Manager, Event, Process
#
#
# class CrawlerMp(Crawler):
#
#     def __init__(self, entrypoint: Any, num_proc: int = 4, *args, **kwargs):
#         self.manager = Manager()
#         self.num_proc = num_proc
#         self.args = args
#         self.kwargs = kwargs
#         self.entrypoint = entrypoint
#         self.metadata = ()
#         # Shared lists
#         self.targets = self.manager.list()
#         self.links = self.manager.list((self.entrypoint,))
#         self.links_followed = self.manager.list()
#         self.links_error = self.manager.list()
#         self.stop_signal = Event()
#         self.workers = []
#
#     def __iter__(self):
#         for i in range(self.num_proc):
#             next_signal = Event()
#             finished_signal = Event()
#             worker = Process(target=self._crawl_worker, args=(next_signal, finished_signal, self.stop_signal))
#             self.workers.append((worker, next_signal, finished_signal))
#             worker.start()
#         return self
#
#     def __next__(self):
#         if len(self.links) > 0:
#             self._worker_next()
#             return self
#         else:
#             self.stop_signal.set()
#             self._worker_next()
#             raise StopIteration
#
#     def _worker_next(self):
#         for _, next_signal, _ in self.workers:
#             next_signal.set()
#         for _, _, finished_signal in self.workers:
#             finished_signal.wait()
#
#     def _crawl_worker(self, next_signal: Event, finished_signal: Event, stop_signal: Event):
#         print("Worker ready!")
#         finished_signal.set()
#         while next_signal.wait():
#             finished_signal.clear()
#             if self.stop_signal.is_set():
#                 finished_signal.set()
#                 print("Worker done!")
#                 return
#             if len(self.links) > 0:
#                 try:
#                     next_link = self.links.pop(0)
#                     self.crawl(next_link)
#                     self.links_followed.append(next_link)
#                 except IndexError:
#                     pass
#                 except Exception as e:
#                     self.links_error.append(next_link)
#                     print(f"Exception entering {self.entrypoint}, ERROR: {e}")
#             next_signal.clear()
#             finished_signal.set()
#
#
#     def _all_workers_done(self):
#         for _, _, finished_signal in self.workers:
#             if not finished_signal.is_set():
#                 return False
#         return True
#
#     def crawl_async(self):
#         self.__iter__()
#         sleep(1)
#         while not self._all_workers_done() or len(self.links) > 0:
#             for _, next_signal, finished_signal in self.workers:
#                 if finished_signal.is_set():
#                     next_signal.set()
#         self.stop_signal.set()
#         for _, next_signal, _ in self.workers:
#             next_signal.set()

    # def crawl(self, entrypoint: Any):
    #     self.entrypoint = entrypoint
    #     metadata = self.init_entrypoint()
    #     targets = self.extract_targets()
    #     links = self.extract_links()
    #     self.close_entrypoint()
    #     return metadata, targets, links
