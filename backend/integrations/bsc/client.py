import httpx
import json
from backend.core.config import settings

VERIFICATION_AMOUNT_BNB = 0.01


async def check_transaction(txid: str, expected_to: str, min_amount: float = VERIFICATION_AMOUNT_BNB) -> bool:
    """Check if a BSC transaction sends at least min_amount BNB to expected_to."""
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getTransactionByHash",
        "params": [txid],
        "id": 1,
    }
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(settings.BSC_RPC_URL, json=payload)
            data = resp.json()
            tx = data.get("result")
            if not tx:
                return False
            to_addr = tx.get("to", "")
            value_hex = tx.get("value", "0x0")
            value_wei = int(value_hex, 16)
            value_bnb = value_wei / 1e18
            return to_addr.lower() == expected_to.lower() and value_bnb >= min_amount
    except Exception:
        return False
