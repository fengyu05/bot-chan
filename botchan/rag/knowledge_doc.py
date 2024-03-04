from enum import Enum
from typing import Optional

from pydantic import BaseModel


class DocKind(Enum):
    TEXT = "TEXT"
    MARK_DOWN = "MARK_DOWN"
    SOURCE = "SOURCE"
    WORD = "WORD"
    PDF = "PDF"
    WEB = "WEB"
    UNRECOGNIZED = "UNRECOGNIZED"


class Doc(BaseModel):
    doc_kind: DocKind
    source_url: Optional[str] = None
    text: Optional[str] = None
    name: Optional[str] = None
