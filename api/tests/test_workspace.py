import pytest
from fastapi.testclient import TestClient
import sys
import os
import uuid

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from main import app
from app.config.db import SessionLocal
from app.models.workspace import Workspaces
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

def delete_test_workspaces(workspace_names):
    """删除测试工作区"""
    db = SessionLocal()
    try:
        for name in workspace_names:
            workspace = db.query(Workspaces).filter(Workspaces.name == name).first()
            if workspace:
                db.delete(workspace)
        db.commit()
    finally:
        db.close()

def delete_test_users(usernames):
    """删除测试用户及其角色关联数据"""
    db = SessionLocal()
    try:
        for username in usernames:
            user = db.query(User).filter(User.username == username).first()
            if user:
                # 先删除用户角色关联数据
                db.query(UserRoles).filter(UserRoles.user_id == user.id).delete()
                # 再删除用户
                db.delete(user)
        db.commit()
    finally:
        db.close()

def test_create_and_manage_workspace(client):
    """测试创建、获取、更新和删除工作区的完整流程"""
    # 生成唯一的用户名和邮箱
    unique_id = str(uuid.uuid4())[:8]
    username = f"workspace_test_user_{unique_id}"
    email = f"workspace_test_{unique_id}@example.com"
    workspace_name = f"Test Workspace {unique_id}"
    workspace_description = "Test workspace for integration testing"
    
    # 先注册用户
    register_resp = client.post("/auth/register", json={
        "username": username,
        "email": email,
        "password": "testpass",
        "full_name": "Workspace Test User"
    })
    assert register_resp.status_code == 200
    
    # 登录获取token
    login_resp = client.post("/auth/token", data={
        "username": username,
        "password": "testpass"
    })
    assert login_resp.status_code == 200
    token = login_resp.json().get("access_token")
    assert token is not None
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 创建工作区
    create_resp = client.post("/workspace/", json={
        "name": workspace_name,
        "description": workspace_description
    }, headers=headers)
    assert create_resp.status_code == 201
    
    workspace_data = create_resp.json()
    workspace_id = workspace_data["id"]
    assert workspace_data["name"] == workspace_name
    assert workspace_data["description"] == workspace_description
    assert "owner_id" in workspace_data
    
    # 获取工作区信息
    get_resp = client.get(f"/workspace/{workspace_id}", headers=headers)
    assert get_resp.status_code == 200
    retrieved_workspace = get_resp.json()
    assert retrieved_workspace["id"] == workspace_id
    assert retrieved_workspace["name"] == workspace_name
    assert retrieved_workspace["description"] == workspace_description
    
    # 更新工作区
    updated_name = f"Updated {workspace_name}"
    update_resp = client.put(f"/workspace/{workspace_id}", json={
        "name": updated_name,
        "description": "Updated description"
    }, headers=headers)
    assert update_resp.status_code == 200
    updated_workspace = update_resp.json()
    assert updated_workspace["name"] == updated_name
    assert updated_workspace["description"] == "Updated description"
    
    # 获取工作区列表
    list_resp = client.get("/workspace/", headers=headers)
    assert list_resp.status_code == 200
    workspaces = list_resp.json()
    assert len(workspaces) >= 1
    workspace_ids = [ws["id"] for ws in workspaces]
    assert workspace_id in workspace_ids
    
    # 删除工作区
    delete_resp = client.delete(f"/workspace/{workspace_id}", headers=headers)
    assert delete_resp.status_code == 204
    
    # 验证工作区已被删除
    get_deleted_resp = client.get(f"/workspace/{workspace_id}", headers=headers)
    assert get_deleted_resp.status_code == 404
    
    # 清理测试数据
    delete_test_workspaces([workspace_name, updated_name])
    delete_test_users([username])

def test_workspace_access_control(client):
    """测试工作区访问控制"""
    # 生成唯一的用户名和邮箱
    unique_id = str(uuid.uuid4())[:8]
    username1 = f"workspace_owner_{unique_id}"
    email1 = f"owner_{unique_id}@example.com"
    username2 = f"workspace_other_{unique_id}"
    email2 = f"other_{unique_id}@example.com"
    workspace_name = f"Access Test Workspace {unique_id}"
    
    # 创建两个用户
    for username, email in [(username1, email1), (username2, email2)]:
        register_resp = client.post("/auth/register", json={
            "username": username,
            "email": email,
            "password": "testpass",
            "full_name": "Test User"
        })
        assert register_resp.status_code == 200
    
    # 用户1登录并创建工作区
    login_resp1 = client.post("/auth/token", data={
        "username": username1,
        "password": "testpass"
    })
    assert login_resp1.status_code == 200
    token1 = login_resp1.json().get("access_token")
    headers1 = {"Authorization": f"Bearer {token1}"}
    
    create_resp = client.post("/workspace/", json={
        "name": workspace_name,
        "description": "Access control test workspace"
    }, headers=headers1)
    assert create_resp.status_code == 201
    workspace_id = create_resp.json()["id"]
    
    # 用户2登录
    login_resp2 = client.post("/auth/token", data={
        "username": username2,
        "password": "testpass"
    })
    assert login_resp2.status_code == 200
    token2 = login_resp2.json().get("access_token")
    headers2 = {"Authorization": f"Bearer {token2}"}
    
    # 用户2尝试访问用户1的工作区应该被拒绝
    get_resp = client.get(f"/workspace/{workspace_id}", headers=headers2)
    assert get_resp.status_code == 403
    
    # 用户2尝试更新用户1的工作区应该被拒绝
    update_resp = client.put(f"/workspace/{workspace_id}", json={
        "name": "Hacked Workspace"
    }, headers=headers2)
    assert update_resp.status_code == 403
    
    # 用户2尝试删除用户1的工作区应该被拒绝
    delete_resp = client.delete(f"/workspace/{workspace_id}", headers=headers2)
    assert delete_resp.status_code == 403
    
    # 清理测试数据
    delete_test_workspaces([workspace_name])
    delete_test_users([username1, username2])

def test_invalid_workspace_id(client):
    """测试无效的工作区ID"""
    # 创建用户并登录
    unique_id = str(uuid.uuid4())[:8]
    username = f"invalid_id_test_{unique_id}"
    email = f"invalid_{unique_id}@example.com"
    
    register_resp = client.post("/auth/register", json={
        "username": username,
        "email": email,
        "password": "testpass",
        "full_name": "Invalid ID Test User"
    })
    assert register_resp.status_code == 200
    
    login_resp = client.post("/auth/token", data={
        "username": username,
        "password": "testpass"
    })
    assert login_resp.status_code == 200
    token = login_resp.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    invalid_workspace_id = "invalid-uuid"
    
    # 尝试获取无效ID的工作区
    get_resp = client.get(f"/workspace/{invalid_workspace_id}", headers=headers)
    assert get_resp.status_code == 400
    
    # 尝试更新无效ID的工作区
    update_resp = client.put(f"/workspace/{invalid_workspace_id}", json={
        "name": "Updated Name"
    }, headers=headers)
    assert update_resp.status_code == 400
    
    # 尝试删除无效ID的工作区
    delete_resp = client.delete(f"/workspace/{invalid_workspace_id}", headers=headers)
    assert delete_resp.status_code == 400
    
    # 清理测试数据
    delete_test_users([username])