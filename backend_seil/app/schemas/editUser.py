from pydantic import BaseModel

class UserUpdateRequest(BaseModel):
    name: str
    email: str
    role: str
    department: str
    is_active: bool

class PasswordResetRequest(BaseModel):
    new_password: str
