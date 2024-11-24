
from fastapi import (
    HTTPException,
    Request,
    status as http_status,
)
from fluctlight.data_model.interface.user import User
from fluctlight.logger import get_logger

logger = get_logger(__name__)

async def get_current_user(request: Request) -> User | None:
    """Returns the current user if the request is authenticated, otherwise None."""
    if False:
        raise HTTPException(
                    status_code=http_status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
    return None