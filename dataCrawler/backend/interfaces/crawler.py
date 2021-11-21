from abc import ABC, abstractmethod
from dumper import Dumper

class Crawler(ABC):

    def __init__(self, entrypoint: str, dumper: Dumper):
        self.entrypoint = entrypoint
        self.dumper = dumper
        self.init_entrypoint()

    @abstractmethod
    def init_entrypoint(self):
        ...

    @abstractmethod
    def extract_data_objects(self) -> list:
        ...

    def store_data_objects(self, data_objects: list):
        for data_object in data_objects:
            self.dumper.dump(data_object)


