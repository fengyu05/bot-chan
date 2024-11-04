from typing import Dict

from pydantic import BaseModel
from slack_sdk.web.slack_response import SlackResponse


class MessageResponse(BaseModel):
    ok: bool
    channel: str
    ts: str
    message: Dict

    @classmethod
    def from_api_response(cls, slack_reponse: SlackResponse) -> "MessageResponse":
        return cls(**slack_reponse.data)


class ReactionResponse(BaseModel):
    ok: bool

    @classmethod
    def from_api_response(cls, slack_reponse: SlackResponse) -> "ReactionResponse":
        return cls(ok=slack_reponse["ok"])
