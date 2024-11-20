import json

from pydantic import BaseModel, ValidationError

from fluctlight.logger import get_logger

logger = get_logger(__name__)


class IntentCandidate(BaseModel):
    understanding: str  # System's interpretation of the message
    intent_primary: str  # Primary intent matching the user's need
    intent_secondary: str | None = None  # Secondary intent somewhat matching the need

    @property
    def perfered_json_serialization(self) -> str:
        return "{" + f"{ self.model_dump_json() }" + "}"


def parse_intent_candidate_json(text: str) -> IntentCandidate | None:
    try:
        data = json.loads(text)
        return IntentCandidate(**data)
    except (json.JSONDecodeError, ValidationError) as e:
        logger.error(f"Error parsing JSON:({text})", err=e)
        return None


EXAMPLE_INTENT_CANDIDATE = IntentCandidate(
    understanding="The user wants to place an order for a product.",
    intent_primary="SHOPPING_ASSIST",
    intent_secondary="CHAT",
)
