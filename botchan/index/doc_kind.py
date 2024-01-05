from enum import Enum


class DocKind(Enum):
    MARK_DOWN = "MARK_DOWN"
    SOURCE = "SOURCE"
    WORD = "WORD"
    UNRECOGNIZED = "UNRECOGNIZED"
