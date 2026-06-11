import httpx
from backend.core.config import settings

VERIFICATION_AMOUNT_TRX = 50


async def check_transaction(txid: str, expected_to: str, min_amount: float = VERIFICATION_AMOUNT_TRX) -> bool:
    """Check if a TRON transaction exists and sends at least min_amount TRX to expected_to."""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{settings.TRON_API_URL}/v1/transactions/{txid}")
            if resp.status_code != 200:
                return False
            data = resp.json()
            raw = data.get("raw_data", {}).get("contract", [{}])[0]
            value = raw.get("parameter", {}).get("value", {})
            to_address = value.get("to_address", "")
            amount_sun = value.get("amount", 0)
            amount_trx = amount_sun / 1_000_000
            return to_address.lower() == expected_to.lower() and amount_trx >= min_amount
    except Exception:
        return False


async def validate_address(address: str) -> bool:
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{settings.TRON_API_URL}/v1/accounts/{address}")
            return resp.status_code == 200
    except Exception:
        return False
