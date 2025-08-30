"""
Workspaces 路由模块

该模块用于定义与 Workspace（工作区）相关的 API 路由。Workspace 等同于租户（Tenant），
用于实现多租户的数据隔离和权限管理。Router 层负责接收客户端请求，调用 Service 层处理
Workspace 的业务逻辑，并返回相应结果。

主要功能包括：
- 提供创建、查询、更新、删除 Workspace 的 API 接口
- 支持 Workspace 与用户、资源的关联操作的路由
- 实现多租户环境下的数据隔离和权限控制的接口入口
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid
from app.config.db import get_db
from app.services.workspace import WorkspaceService
from app.models.workspace import WorkspaceCreate, WorkspaceRead, WorkspaceUpdate
from app.models.auth import User, UserRead
from app.services.auth import AuthService
from app.utils.schema import BaseResponse, PageResponse

router = APIRouter()
auth_service = AuthService()

# -------------------- Routes --------------------

@router.post("/", response_model=BaseResponse[WorkspaceRead], status_code=status.HTTP_201_CREATED)
def create_workspace(
    workspace: WorkspaceCreate,
    current_user: UserRead = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建新的工作区
    只有经过身份验证的用户才能创建工作区，并且该用户将成为工作区的所有者
    """
    workspace_service = WorkspaceService(db)
    try:
        owner_id = current_user.id
        db_workspace = workspace_service.create_workspace(workspace, owner_id)
        return BaseResponse[WorkspaceRead](data=db_workspace)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{workspace_id}", response_model=BaseResponse[WorkspaceRead])
def read_workspace(
    workspace_id: str,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """
    根据ID获取单个工作区信息
    只有工作区的所有者或授权用户才能访问
    """
    try:
        workspace_uuid = uuid.UUID(workspace_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid workspace ID format"
        )
    
    workspace_service = WorkspaceService(db)
    workspace = workspace_service.get_workspace(workspace_uuid)
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )
    
    # 检查用户是否有权限访问该工作区
    if workspace.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this workspace"
        )
    
    return BaseResponse[WorkspaceRead](data=workspace)

@router.get("/", response_model=BaseResponse[PageResponse[WorkspaceRead]])
def read_workspaces(
    skip: int = 0,
    limit: int = 100,
    current_user: UserRead = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户拥有的工作区列表
    """
    workspace_service = WorkspaceService(db)
    owner_id = current_user.id
    workspaces = workspace_service.get_workspaces_by_owner(owner_id, skip, limit)
    
    # 计算总数以支持分页
    total_workspaces = len(workspace_service.get_workspaces_by_owner(owner_id, 0, 10000))  # 获取所有工作区数量
    
    # 构造分页响应
    page_response = PageResponse[WorkspaceRead](
        items=workspaces,
        total=total_workspaces,
        page=skip // limit + 1,
        size=limit,
        has_next=(skip + limit) < total_workspaces,
        has_prev=skip > 0
    )
    
    return BaseResponse[PageResponse[WorkspaceRead]](data=page_response)

@router.put("/{workspace_id}", response_model=BaseResponse[WorkspaceRead])
def update_workspace(
    workspace_id: str,
    workspace_update: WorkspaceUpdate,
    current_user: UserRead = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新工作区信息
    只有工作区的所有者才能更新工作区信息
    """
    try:
        workspace_uuid = uuid.UUID(workspace_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid workspace ID format"
        )
    
    workspace_service = WorkspaceService(db)
    workspace = workspace_service.get_workspace(workspace_uuid)
    
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )
    
    # 检查用户是否有权限更新该工作区
    if workspace.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this workspace"
        )
    
    updated_workspace = workspace_service.update_workspace(workspace_uuid, workspace_update)
    if not updated_workspace:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update workspace"
        )
    
    return BaseResponse[WorkspaceRead](data=updated_workspace)

@router.delete("/{workspace_id}", response_model=BaseResponse[dict])
def delete_workspace(
    workspace_id: str,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除工作区
    只有工作区的所有者才能删除工作区
    """
    try:
        workspace_uuid = uuid.UUID(workspace_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid workspace ID format"
        )
    
    workspace_service = WorkspaceService(db)
    workspace = workspace_service.get_workspace(workspace_uuid)
    
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )
    
    # 检查用户是否有权限删除该工作区
    if workspace.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete this workspace"
        )
    
    success = workspace_service.delete_workspace(workspace_uuid)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete workspace"
        )
    
    return BaseResponse[dict](data={"message": "Workspace deleted successfully"})