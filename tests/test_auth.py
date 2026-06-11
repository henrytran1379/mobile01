import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    resp = await client.post("/api/v1/auth/register", json={"email": "test@example.com"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["success"] is True
    assert "user_code" in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    await client.post("/api/v1/auth/register", json={"email": "dup@example.com"})
    resp = await client.post("/api/v1/auth/register", json={"email": "dup@example.com"})
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_register_invalid_email(client: AsyncClient):
    resp = await client.post("/api/v1/auth/register", json={"email": "not-an-email"})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    await client.post("/api/v1/auth/register", json={"email": "login@example.com"})
    resp = await client.post("/api/v1/auth/login", json={"email": "login@example.com", "password": "wrong"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_first_time_requires_password_change(client: AsyncClient, db_session):
    from backend.services.auth_service import AuthService

    svc = AuthService(db_session)
    result = await svc.register("firstlogin@example.com")
    temp_pw = result["temp_password"]
    await db_session.commit()

    resp = await client.post("/api/v1/auth/login", json={"email": "firstlogin@example.com", "password": temp_pw})
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("requires_password_change") is True


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
