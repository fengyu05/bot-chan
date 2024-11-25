from typing import Optional

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    id: Optional[int] = (
        None  # Assuming the ID is generated automatically by the database
    )
    name: str
    email: EmailStr
