from enum import Enum


class Mode(Enum):
    SIMPLE = "s"
    EXTENDED = "e"

class Header(Enum):
    PATH = "Path"
    NAME = "Name"
    SIZE = "Size"
    MODIFIED = "Modified"
    ACCESSED = "Accessed"