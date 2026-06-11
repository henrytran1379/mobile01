from pydantic import BaseModel
from typing import Optional


class AddWalletRequest(BaseModel):
    network: str
    address: str
    wallet_type: str = "PRIMARY"


class WalletResponse(BaseModel):
    wallet_id: str
    network: str
    address: str
    type: str
    status: str
    verified_at: Optional[str] = None


class WalletVerifyRequest(BaseModel):
    txid: Optional[str] = None
