from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class UserListItem(BaseModel):
    id: str
    name: str
    email: str
    role: str
    is_active: bool
    last_login_at: Optional[datetime]
    department: Optional[str]


class UserListResponse(BaseModel):
    users: List[UserListItem]
