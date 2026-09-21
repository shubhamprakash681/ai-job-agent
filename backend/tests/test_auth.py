import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_setup_status_no_users(client: AsyncClient):
    response = await client.get("/api/auth/setup/status")
    assert response.status_code == 200
    assert response.json()["is_setup"] == False

@pytest.mark.asyncio
async def test_setup_creates_user(client: AsyncClient):
    response = await client.post("/api/auth/setup", json={
        "email": "admin@example.com",
        "password": "securepassword",
        "full_name": "Admin User"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "admin@example.com"

@pytest.mark.asyncio
async def test_setup_twice_fails(client: AsyncClient):
    await client.post("/api/auth/setup", json={
        "email": "admin1@example.com",
        "password": "securepassword",
        "full_name": "Admin User 1"
    })
    
    response = await client.post("/api/auth/setup", json={
        "email": "admin2@example.com",
        "password": "securepassword",
        "full_name": "Admin User 2"
    })
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    await client.post("/api/auth/setup", json={
        "email": "admin@example.com",
        "password": "securepassword",
        "full_name": "Admin User"
    })
    
    response = await client.post("/api/auth/login", json={
        "email": "admin@example.com",
        "password": "securepassword"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    await client.post("/api/auth/setup", json={
        "email": "admin@example.com",
        "password": "securepassword",
        "full_name": "Admin User"
    })
    
    response = await client.post("/api/auth/login", json={
        "email": "admin@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_me_authenticated(client: AsyncClient, auth_headers: dict):
    response = await client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"

@pytest.mark.asyncio
async def test_me_unauthenticated(client: AsyncClient):
    response = await client.get("/api/auth/me")
    assert response.status_code == 401
