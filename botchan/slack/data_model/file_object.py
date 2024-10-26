from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class Preview(BaseModel):
    content: str
    has_more: bool


class Transcription(BaseModel):
    status: str
    locale: Optional[str] = None
    preview: Optional[Preview] = None


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
    original_w: Optional[int] = None
    original_h: Optional[int] = None

    # thumb
    thumb_64: Optional[str] = None
    thumb_80: Optional[str] = None
    thumb_360: Optional[str] = None
    thumb_360_w: Optional[int] = None
    thumb_360_h: Optional[int] = None
    thumb_480: Optional[str] = None
    thumb_480_w: Optional[int] = None
    thumb_480_h: Optional[int] = None
    thumb_160: Optional[str] = None
    thumb_720: Optional[str] = None
    thumb_720_w: Optional[int] = None
    thumb_720_h: Optional[int] = None
    thumb_800: Optional[str] = None
    thumb_800_w: Optional[int] = None
    thumb_800_h: Optional[int] = None
    thumb_960: Optional[str] = None
    thumb_960_w: Optional[int] = None
    thumb_960_h: Optional[int] = None
    thumb_1024: Optional[str] = None
    thumb_1024_w: Optional[int] = None
    thumb_1024_h: Optional[int] = None
    thumb_tiny: Optional[str] = None
    thumb_pdf: Optional[str] = None
    thumb_pdf_w: Optional[int] = None
    thumb_pdf_h: Optional[int] = None
    # thumb end

    # audio
    subtype: Optional[str] = None
    duration_ms: Optional[int] = None
    aac: Optional[str] = None
    audio_wave_samples: Optional[List[int]] = None
    transcription: Optional[Transcription] = None
    # audio end

    permalink: str
    permalink_public: str
    has_rich_preview: bool
    file_access: str

    def get_transcription_preview(self) -> Optional[str]:
        if (
            self.transcription
            and self.transcription.status == "complete"
            and self.transcription.preview
        ):
            return self.transcription.preview.content
        else:
            return None
