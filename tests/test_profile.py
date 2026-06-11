import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from backend.repositories.user_repository import UserRepository
from backend.services.profile_service import ProfileService


@pytest.mark.asyncio
async def test_get_empty_profile(db_session: AsyncSession):
    repo = UserRepository(db_session)
    user = await repo.create(email="profile@test.com", user_code="USR010", status="ACTIVE", role="USER")

    svc = ProfileService(db_session)
    profile = await svc.get_profile(str(user.id))
    assert profile["full_name"] is None
    assert profile["identity_number"] is None


@pytest.mark.asyncio
async def test_update_profile(db_session: AsyncSession):
    repo = UserRepository(db_session)
    user = await repo.create(email="profile2@test.com", user_code="USR011", status="ACTIVE", role="USER")

    svc = ProfileService(db_session)
    await svc.update_profile(str(user.id), {"full_name": "Nguyen Van A", "gender": "MALE"})

    profile = await svc.get_profile(str(user.id))
    assert profile["full_name"] == "Nguyen Van A"
    assert profile["gender"] == "MALE"
