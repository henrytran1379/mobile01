import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from backend.repositories.profile_repository import UserProfileRepository, IdentityDocumentRepository
from backend.repositories.audit_repository import AuditLogRepository


class ProfileService:
    def __init__(self, session: AsyncSession):
        self.profile_repo = UserProfileRepository(session)
        self.identity_repo = IdentityDocumentRepository(session)
        self.audit_repo = AuditLogRepository(session)

    async def get_profile(self, user_id: str) -> dict:
        uid = uuid.UUID(user_id)
        profile = await self.profile_repo.get_by_user_id(uid)
        identity = await self.identity_repo.get_by_user_id(uid)

        def mask(value: str | None, visible: int = 3) -> str | None:
            if not value:
                return None
            return value[:visible] + "*" * (len(value) - visible)

        return {
            "full_name": profile.full_name if profile else None,
            "date_of_birth": str(profile.date_of_birth) if profile and profile.date_of_birth else None,
            "gender": profile.gender if profile else None,
            "nationality": profile.nationality if profile else None,
            "avatar_url": profile.avatar_url if profile else None,
            "identity_number": mask(identity.identity_number, 3) if identity else None,
        }

    async def update_profile(self, user_id: str, data: dict, ip_address: str | None = None) -> dict:
        uid = uuid.UUID(user_id)
        allowed_fields = {"full_name", "date_of_birth", "gender", "nationality", "avatar_url"}
        update_data = {k: v for k, v in data.items() if k in allowed_fields and v is not None}

        await self.profile_repo.upsert(uid, **update_data)

        await self.audit_repo.log(
            action="PROFILE_UPDATED",
            actor_type="USER",
            actor_id=uid,
            target_id=uid,
            target_type="USER",
            ip_address=ip_address,
        )
        return {"success": True}
