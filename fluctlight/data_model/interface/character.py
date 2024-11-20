from dataclasses import dataclass

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
