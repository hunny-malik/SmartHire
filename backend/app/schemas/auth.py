from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    target_role: Optional[str] = None
    language_preference: Optional[str] = "English"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    target_role: Optional[str] = None
    language_preference: Optional[str] = None

class UserOut(BaseModel):
    id: str
    email: str
    full_name: str
    target_role: Optional[str] = None
    language_preference: str = "English"
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
