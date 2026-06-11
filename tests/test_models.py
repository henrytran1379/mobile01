import pytest
import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.user import User, UserStatus
from backend.models.security import UserSecurity
from backend.repositories.user_repository import UserRepository
from backend.repositories.security_repository import UserSecurityRepository
from backend.repositories.credit_repository import CreditAccountRepository
from backend.security.password import hash_password


@pytest.mark.asyncio
async def test_create_and_get_user(db_session: AsyncSession):
    repo = UserRepository(db_session)
    user = await repo.create(
        email="test@test.com",
        user_code="USR001",
        status=UserStatus.ACCOUNT_CREATED,
        role="USER",
    )
    assert user.id is not None
    assert user.email == "test@test.com"

    found = await repo.get_by_email("test@test.com")
    assert found is not None
    assert found.id == user.id


@pytest.mark.asyncio
async def test_email_exists(db_session: AsyncSession):
    repo = UserRepository(db_session)
    await repo.create(email="exists@test.com", user_code="USR002", status="ACTIVE", role="USER")
    assert await repo.email_exists("exists@test.com") is True
    assert await repo.email_exists("notexists@test.com") is False


@pytest.mark.asyncio
async def test_credit_account_get_or_create(db_session: AsyncSession):
    user_repo = UserRepository(db_session)
    user = await user_repo.create(email="credit@test.com", user_code="USR003", status="ACTIVE", role="USER")

    credit_repo = CreditAccountRepository(db_session)
    account = await credit_repo.get_or_create(user.id)
    assert account.balance == 0

    account2 = await credit_repo.get_or_create(user.id)
    assert account2.id == account.id


@pytest.mark.asyncio
async def test_credit_adjust_balance(db_session: AsyncSession):
    user_repo = UserRepository(db_session)
    user = await user_repo.create(email="bal@test.com", user_code="USR004", status="ACTIVE", role="USER")

    credit_repo = CreditAccountRepository(db_session)
    await credit_repo.get_or_create(user.id)
    account = await credit_repo.adjust_balance(user.id, 100)
    assert account.balance == 100

    with pytest.raises(ValueError):
        await credit_repo.adjust_balance(user.id, -200)
