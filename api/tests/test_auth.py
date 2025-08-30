import pytest
from fastapi.testclient import TestClient
import sys
import os
import uuid

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from main import app
from app.config.db import SessionLocal
from app.models.auth import User, UserRoles

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="function")
def db_session():
    """创建数据库会话用于测试"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def delete_test_users(usernames: list[str]):
    """
    安全地删除测试用户及其关联的角色数据
    
    参数:
        usernames (list[str]): 要删除的用户名列表
    
    注意: 该函数会静默忽略不存在的用户名
    """
    if not isinstance(usernames, list):
        raise TypeError("usernames参数必须是列表类型")
        
    db = SessionLocal()
    try:
        # 批量查询用户
        users = db.query(User).filter(User.username.in_(usernames)).all()
        
        # 收集存在的用户ID
        user_ids = [user.id for user in users]
        
        # 如果有存在的用户，先删除用户角色关联数据
        if user_ids:
            db.query(UserRoles).filter(UserRoles.user_id.in_(user_ids)).delete()
        
        # 按用户名逐个删除用户，确保清理干净
        for username in usernames:
            db.query(User).filter(User.username == username).delete()
        
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"清理测试用户时发生错误: {str(e)}")
    finally:
        db.close()

def test_register_and_login(client):
    # 生成唯一的用户名和邮箱，避免重复注册错误
    unique_id = str(uuid.uuid4())[:8]
    username = f"testuser_{unique_id}"
    email = f"testuser_{unique_id}@example.com"
    
    # 注册
    resp = client.post("/auth/register", json={
        "username": username,
        "email": email,
        "password": "testpass",
        "full_name": "Test User"
    })
    print(f"Register status: {resp.status_code}")
    print(f"Register response: {resp.json()}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == username
    assert data["email"] == email

    # 登录
    resp = client.post("/auth/token", data={
        "username": username,
        "password": "testpass"
    })
    print(f"Login status: {resp.status_code}")
    print(f"Login response: {resp.json()}")
    assert resp.status_code == 200
    token = resp.json().get("access_token")
    assert token is not None

    # 使用token获取当前用户信息
    resp = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    user_data = resp.json()
    assert user_data["username"] == username
    assert user_data["email"] == email
    assert "id" in user_data
    assert "created_at" in user_data
    assert "updated_at" in user_data

    # 清理测试数据
    delete_test_users([username])

def test_register_duplicate_username(client):
    # 生成唯一的用户名和邮箱
    unique_id = str(uuid.uuid4())[:8]
    username = f"dup_testuser_{unique_id}"
    email1 = f"test1_{unique_id}@example.com"
    email2 = f"test2_{unique_id}@example.com"
    
    # 第一次注册
    resp1 = client.post("/auth/register", json={
        "username": username,
        "email": email1,
        "password": "testpass",
        "full_name": "Test User"
    })
    assert resp1.status_code == 200
    
    # 尝试用相同用户名注册
    resp2 = client.post("/auth/register", json={
        "username": username,
        "email": email2,
        "password": "testpass",
        "full_name": "Test User"
    })
    assert resp2.status_code == 400
    assert resp2.json()["detail"] == "Username already registered"

    # 清理测试数据
    delete_test_users([username])

def test_register_duplicate_email(client):
    # 生成唯一的用户名和邮箱
    unique_id = str(uuid.uuid4())[:8]
    username1 = f"testuser1_{unique_id}"
    username2 = f"testuser2_{unique_id}"
    email = f"dup_email_{unique_id}@example.com"
    
    # 第一次注册
    resp1 = client.post("/auth/register", json={
        "username": username1,
        "email": email,
        "password": "testpass",
        "full_name": "Test User"
    })
    assert resp1.status_code == 200
    
    # 尝试用相同邮箱注册
    resp2 = client.post("/auth/register", json={
        "username": username2,
        "email": email,
        "password": "testpass",
        "full_name": "Test User"
    })
    assert resp2.status_code == 400
    assert resp2.json()["detail"] == "Email already registered"

    # 清理测试数据
    delete_test_users([username1, username2])

def test_login_with_invalid_credentials(client):
    # 生成唯一的用户名
    unique_id = str(uuid.uuid4())[:8]
    username = f"invalid_cred_user_{unique_id}"
    
    # 尝试使用无效凭据登录
    resp = client.post("/auth/token", data={
        "username": username,
        "password": "wrongpass"
    })
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Incorrect username or password"

def test_reset_password(client):
    # 生成唯一的用户名和邮箱
    unique_id = str(uuid.uuid4())[:8]
    username = f"reset_pass_user_{unique_id}"
    email = f"reset_{unique_id}@example.com"
    
    # 先注册用户
    register_resp = client.post("/auth/register", json={
        "username": username,
        "email": email,
        "password": "oldpass",
        "full_name": "Test User"
    })
    assert register_resp.status_code == 200
    
    # 重置密码
    reset_resp = client.post("/auth/reset-password", json={
        "username": username,
        "new_password": "newpass"
    })
    assert reset_resp.status_code == 200
    assert reset_resp.json()["msg"] == "Password reset successful"
    
    # 使用新密码登录
    login_resp = client.post("/auth/token", data={
        "username": username,
        "password": "newpass"
    })
    assert login_resp.status_code == 200
    token = login_resp.json().get("access_token")
    assert token is not None

    # 清理测试数据
    delete_test_users([username])