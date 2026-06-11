from pydantic import BaseModel
from typing import Optional


class ReviewActionRequest(BaseModel):
    reason: Optional[str] = None


class CreditAdjustRequest(BaseModel):
    user_id: str
    amount: int
    reason: str
