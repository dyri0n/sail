from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class UserStatsResponse(BaseModel):
    total_users: int
    active_users: int
    admin_users: int
    last_access: Optional[datetime]
