from abc import ABC, abstractmethod

from dumper import Dumper


class Crawler(ABC):

    def __init__(self, entrypoint: str, dumper: Dumper):
        self.entrypoint = entrypoint
        self.dumper = dumper
        self.metadata = self.init_entrypoint()
        extracted_objects = self.extract_data_objects()
        self.links = self.extract_links()
        self.store_data_objects(extracted_objects)
        self.close_entrypoint()

    @abstractmethod
    def init_entrypoint(self) -> tuple:
        ...

    @abstractmethod
    def extract_data_objects(self) -> list:
        ...

    def extract_links(self) -> list:
        ...

    def store_data_objects(self, data_objects: list):
        for data_object in data_objects:
            self.dumper.dump(data_object)

    @abstractmethod
    def close_entrypoint(self):
        ...
