from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class FileObject(BaseModel):
    id: str
    created: int
    timestamp: int
    name: str
    title: str
    mimetype: str
    filetype: str
    pretty_type: str
    user: str
    user_team: str
    editable: bool
    size: int
    mode: str
    is_external: bool
    external_type: str
    is_public: bool
    public_url_shared: bool
    display_as_bot: bool
    username: str
    url_private: str
    url_private_download: str
    media_display_type: str
    original_w: Optional[int]
    original_h: Optional[int]
    # thumb
    thumb_64: Optional[str]
    thumb_80: Optional[str]
    thumb_360: Optional[str]
    thumb_360_w: Optional[int]
    thumb_360_h: Optional[int]
    thumb_480: Optional[str]
    thumb_480_w: Optional[int]
    thumb_480_h: Optional[int]
    thumb_160: Optional[str]
    thumb_720: Optional[str]
    thumb_720_w: Optional[int]
    thumb_720_h: Optional[int]
    thumb_800: Optional[str]
    thumb_800_w: Optional[int]
    thumb_800_h: Optional[int]
    thumb_960: Optional[str]
    thumb_960_w: Optional[int]
    thumb_960_h: Optional[int]
    thumb_1024: Optional[str]
    thumb_1024_w: Optional[int]
    thumb_1024_h: Optional[int]
    thumb_tiny: Optional[str]
    thumb_pdf: Optional[str]
    thumb_pdf_w: Optional[int]
    thumb_pdf_h: Optional[int]
    # thumb end

    # audio
    subtype: Optional[str]
    duration_ms: Optional[int]
    aac: Optional[str]
    audio_wave_samples: Optional[List[int]]
    transcription: Optional[Dict[str, Any]]
    # audio end

    permalink: str
    permalink_public: str
    has_rich_preview: bool
    file_access: str
