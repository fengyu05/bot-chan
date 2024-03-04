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
    thumb_pdf: str
    thumb_pdf_w: int
    thumb_pdf_h: int
    permalink: str
    permalink_public: str
    has_rich_preview: bool
    file_access: str
