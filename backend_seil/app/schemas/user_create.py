from pydantic import BaseModel, EmailStr
from typing import Optional


class UserCreateRequest(BaseModel):
    name: str
    email: EmailStr
    username: str
    role: str  # ADMIN | GERENCIA
    department: Optional[str] = None
