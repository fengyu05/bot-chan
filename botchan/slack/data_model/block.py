from typing import Optional, List
from pydantic import BaseModel


class RichTextSectionElement(BaseModel):
    type: str
    text: Optional[str] = None
    user: Optional[str] = None


class RichTextSection(BaseModel):
    elements: List[RichTextSectionElement]


class RichTextBlock(BaseModel):
    block_id: str
    elements: List[RichTextSection]
