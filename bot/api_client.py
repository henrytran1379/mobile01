"""HTTP client gọi FastAPI backend."""
import httpx
from backend.core.config import settings

BASE_URL = "http://localhost:8001/api/v1"
TIMEOUT = 30


async def _post(path: str, data: dict, token: str = None) -> dict:
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        r = await client.post(f"{BASE_URL}{path}", json=data, headers=headers)
        return r.json()


async def _get(path: str, token: str, params: dict = None) -> dict:
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        r = await client.get(f"{BASE_URL}{path}", headers=headers, params=params)
        return r.json()


async def register(email: str) -> dict:
    return await _post("/auth/register", {"email": email})


async def resend_verification(email: str) -> dict:
    return await _post("/auth/resend-verification-email", {"email": email})


async def login(email: str, password: str) -> dict:
    return await _post("/auth/login", {"email": email, "password": password})


async def first_login_change_password(user_id: str, old_pw: str, new_pw: str) -> dict:
    return await _post("/auth/first-login-change-password", {
        "user_id": user_id, "old_password": old_pw, "new_password": new_pw,
    })


async def change_password(token: str, old_pw: str, new_pw: str) -> dict:
    return await _post("/auth/change-password", {"old_password": old_pw, "new_password": new_pw}, token)


async def setup_2fa(token: str) -> dict:
    return await _post("/auth/2fa/setup", {}, token)


async def verify_2fa_setup(token: str, code: str) -> dict:
    return await _post("/auth/2fa/verify", {"code": code}, token)


async def login_2fa(pending_token: str, code: str) -> dict:
    return await _post("/auth/2fa/login", {"pending_token": pending_token, "code": code})


async def get_profile(token: str) -> dict:
    return await _get("/profile", token)


async def update_profile(token: str, data: dict) -> dict:
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        r = await client.put(f"{BASE_URL}/profile", json=data, headers=headers)
        return r.json()


async def get_kyc_status(token: str) -> dict:
    return await _get("/kyc/status", token)


async def get_ekyc_status(token: str) -> dict:
    return await _get("/ekyc/status", token)


async def submit_kyc_full(
    token: str,
    telegram_user_id: int,
    front_bytes: bytes,
    back_bytes: bytes,
    portrait_bytes: bytes,
) -> dict:
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Telegram-User-Id": str(telegram_user_id),
    }
    files = {
        "front":    ("front.jpg",    front_bytes,    "image/jpeg"),
        "back":     ("back.jpg",     back_bytes,     "image/jpeg"),
        "portrait": ("portrait.jpg", portrait_bytes, "image/jpeg"),
    }
    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(f"{BASE_URL}/kyc/submit", files=files, headers=headers)
        return r.json()


async def get_kyc_queue(token: str) -> dict:
    return await _get("/kyc/admin/queue", token)


async def get_kyc_detail(token: str, kyc_profile_id: str) -> dict:
    return await _get(f"/kyc/admin/{kyc_profile_id}", token)


async def kyc_approve(token: str, kyc_profile_id: str) -> dict:
    return await _post(f"/kyc/admin/{kyc_profile_id}/approve", {}, token)


async def kyc_reject(token: str, kyc_profile_id: str, reason: str) -> dict:
    return await _post(f"/kyc/admin/{kyc_profile_id}/reject", {"reason": reason}, token)


async def submit_ekyc(token: str, pdf_bytes: bytes) -> dict:
    headers = {"Authorization": f"Bearer {token}"}
    files = {"pdf": ("ekyc.pdf", pdf_bytes, "application/pdf")}
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(f"{BASE_URL}/ekyc/upload", files=files, headers=headers)
        return r.json()


async def get_kyc_vneid_status(token: str) -> dict:
    return await _get("/kyc/vneid/status", token)


async def submit_kyc_vneid(token: str, data: dict) -> dict:
    return await _post("/kyc/vneid/submit", data, token)


async def submit_kycvneid2(token: str, data: dict) -> dict:
    return await _post("/kyc/vneid2/submit", data, token)


async def get_kycvneid2_status(token: str) -> dict:
    return await _get("/kyc/vneid2/status", token)


async def list_wallets(token: str) -> list:
    return await _get("/wallets", token)


async def add_wallet(token: str, network: str, address: str) -> dict:
    return await _post("/wallets", {"network": network, "address": address}, token)


async def get_credits(token: str) -> dict:
    return await _get("/credits/balance", token)


async def get_ledger(token: str) -> list:
    return await _get("/credits/ledger", token)


async def get_reviews(token: str, review_type: str = None) -> list:
    params = {"review_type": review_type} if review_type else None
    return await _get("/admin/reviews", token, params)


async def approve_review(token: str, review_id: str) -> dict:
    return await _post(f"/admin/reviews/{review_id}/approve", {}, token)


async def reject_review(token: str, review_id: str, reason: str) -> dict:
    return await _post(f"/admin/reviews/{review_id}/reject", {"reason": reason}, token)
