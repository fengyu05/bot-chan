from dataclasses import dataclass
from typing import Optional

from pydantic import BaseModel
@dataclass
class Character:
    character_id: str
    name: str
    llm_system_prompt: str
    llm_user_prompt: str
    source: str = ""
    location: str = ""
    voice_id: str = ""
    author_name: str = ""
    author_id: str = ""
    visibility: str = ""
    tts: str | None = ""
    order: int = 10**9  # display order on the website
    data: dict | None = None
    rebyte_api_project_id: str | None = None
    rebyte_api_agent_id: str | None = None
    rebyte_api_version: int | None = None


class CharacterRequest(BaseModel):
    name: str
    system_prompt: Optional[str] = None
    user_prompt: Optional[str] = None
    tts: Optional[str] = None
    voice_id: Optional[str] = None
    visibility: Optional[str] = None
    data: Optional[dict] = None
    avatar_id: Optional[str] = None
    background_text: Optional[str] = None
    rebyte_api_project_id: Optional[str] = None
    rebyte_api_agent_id: Optional[str] = None
    rebyte_api_version: Optional[int] = None


class EditCharacterRequest(BaseModel):
    id: str
    name: Optional[str] = None
    system_prompt: Optional[str] = None
    user_prompt: Optional[str] = None
    tts: Optional[str] = None
    voice_id: Optional[str] = None
    visibility: Optional[str] = None
    data: Optional[dict] = None
    avatar_id: Optional[str] = None
    background_text: Optional[str] = None
    rebyte_api_project_id: Optional[str] = None
    rebyte_api_agent_id: Optional[str] = None
    rebyte_api_version: Optional[int] = None


class DeleteCharacterRequest(BaseModel):
    character_id: str
