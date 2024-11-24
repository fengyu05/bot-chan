from pydantic import BaseModel, EmailStr
from typing import Optional

class User(BaseModel):
    id: Optional[int] = None  # Assuming the ID is generated automatically by the database
    name: str
    email: EmailStr
