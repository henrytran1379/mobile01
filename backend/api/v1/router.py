from fastapi import APIRouter
from backend.api.v1.auth.routes import router as auth_router
from backend.api.v1.profile.routes import router as profile_router
from backend.api.v1.kyc.routes import router as kyc_router
from backend.api.v1.wallet.routes import router as wallet_router
from backend.api.v1.credits.routes import router as credits_router
from backend.api.v1.admin.routes import router as admin_router

v1_router = APIRouter(prefix="/api/v1")
v1_router.include_router(auth_router)
v1_router.include_router(profile_router)
v1_router.include_router(kyc_router)
v1_router.include_router(wallet_router)
v1_router.include_router(credits_router)
v1_router.include_router(admin_router)
