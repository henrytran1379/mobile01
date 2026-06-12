from pydantic import BaseModel, field_validator, AnyHttpUrl, Field
from typing import Optional, Literal
import datetime as dt


class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    date_of_birth: Optional[dt.date] = None
    gender: Optional[Literal["NAM", "NU", "KHAC"]] = None
    nationality: Optional[str] = Field(None, max_length=100)
    avatar_url: Optional[AnyHttpUrl] = None

    @field_validator("full_name", mode="before")
    @classmethod
    def strip_name(cls, v):
        if v is None:
            return v
        stripped = str(v).strip()
        if not stripped:
            raise ValueError("full_name không được để trống")
        return stripped

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, v: dt.date | None) -> dt.date | None:
        if v is None:
            return v
        today = dt.date.today()
        if v >= today:
            raise ValueError("Ngày sinh phải là ngày trong quá khứ")
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        if age < 16:
            raise ValueError("Người dùng phải đủ 16 tuổi")
        if age > 120:
            raise ValueError("Ngày sinh không hợp lệ")
        return v


class ProfileResponse(BaseModel):
    full_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None
    avatar_url: Optional[str] = None
    identity_number: Optional[str] = None
