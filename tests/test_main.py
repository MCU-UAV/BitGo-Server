import pytest
from httpx import AsyncClient
from main import app


@pytest.mark.asyncio
async def test_register():
    username = "testuser"
    async with AsyncClient(app=app,  base_url="https://localhost:8000", verify=False) as client:
        # 测试用户注册
        response = await client.post("/register/", json={"username":username, "password": "password123"})
        assert response.status_code == 200
        assert response.json()["username"] == username


@pytest.mark.asyncio
async def test_login():
    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        # 测试用户登录
        response = await client.post("/token", data={"username": "testuser", "password": "password123"})
        assert response.status_code == 200
        assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_get_user_info():
    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        # 登录获取 token
        token_response = await client.post("/token", data={"username": "testuser", "password": "password123"})
        token = token_response.json()["access_token"]

        # 测试获取当前用户信息
        response = await client.get("/users/me/", headers={"Authorization": f"Bearer {token}"})
        print(response.content)
        assert response.status_code == 200
        assert response.json()["username"] == "testuser"
