from pydantic import BaseModel
from datetime import date
from typing import Optional


class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None
    avatar_url: Optional[str] = None


class ProfileResponse(BaseModel):
    full_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None
    avatar_url: Optional[str] = None
    identity_number: Optional[str] = None
