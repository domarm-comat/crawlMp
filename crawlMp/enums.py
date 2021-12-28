from enum import Enum
from typing import Tuple, Type, Optional


class Mode(Enum):
    SIMPLE = "s"
    EXTENDED = "e"

    def __str__(self) -> str:
        return self.value


class Header(Enum):
    PATH = "Path"
    NAME = "Name"
    SIZE = "Size"
    MODIFIED = "Modified"
    ACCESSED = "Accessed"
    INPUT = "Input"
    OUTPUT = "Output"

    def __str__(self) -> str:
        return self.value


Header_ref = Tuple[Header, Type, Optional[str]]
