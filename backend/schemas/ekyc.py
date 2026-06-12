from pydantic import BaseModel, field_validator
from typing import Optional
import re


class EKYCResultRequest(BaseModel):
    identity_number: str
    full_name: str
    date_of_birth: str          # DD/MM/YYYY
    gender: str
    hometown: Optional[str] = None
    issue_date: str             # DD/MM/YYYY
    expiry_date: str            # DD/MM/YYYY
    permanent_address: Optional[str] = None
    is_real_person: bool = True
    face_matched: bool = True
    provider_name: Optional[str] = None
    provider_reference: Optional[str] = None

    @field_validator("date_of_birth", "issue_date", "expiry_date")
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        if not re.match(r"^\d{2}/\d{2}/\d{4}$", v):
            raise ValueError("Date must be in DD/MM/YYYY format")
        return v


class EKYCResultResponse(BaseModel):
    submission_id: str
    status: str
