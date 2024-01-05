from typing import Optional

from pydantic import BaseModel


class BotProfile(BaseModel):
    id: str
    app_id: str
    name: str
    image_36: Optional[str]
    image_48: Optional[str]
    image_72: Optional[str]
    deleted: bool
    updated: int
    team_id: str
