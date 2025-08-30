"""
Workspaces 服务模块
    Workspace 等同于租户
该模块用于管理和操作 Workspace（工作区），Workspace 等同于租户（Tenant），
用于实现多租户的数据隔离和权限管理。Service 层负责处理与 Workspace 相关的业务逻辑，
包括创建、查询、更新、删除工作区，以及与用户、资源等的关联操作。
主要功能包括：
- 创建和初始化新的 Workspace
- 查询和管理现有 Workspace
- 处理 Workspace 与用户、资源的关联关系
- 提供多租户环境下的数据隔离和权限控制支持
"""

import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.workspace import Workspaces, WorkspaceCreate, WorkspaceRead, WorkspaceUpdate,WorkspaceUsers
from app.models.auth import User


class WorkspaceService:
    """
    Workspace服务类，提供对工作区的完整CRUD操作
    """

    def __init__(self, db: Session):
        """
        初始化Workspace服务

        Args:
            db: 数据库会话实例
        """
        self.db = db

    def create_workspace(self, workspace: WorkspaceCreate, owner_id: uuid.UUID) -> WorkspaceRead:
        """
        创建新的工作区

        Args:
            workspace: 工作区创建模型，包含要创建的工作区信息
            owner_id: 工作区所有者的用户ID

        Returns:
            WorkspaceRead: 创建后的工作区读取模型
        """
        db_workspace = Workspaces(
            **workspace.model_dump(exclude_unset=True),
            owner_id=owner_id
        )
        self.db.add(db_workspace)
        self.db.commit()
        self.db.refresh(db_workspace)
        return WorkspaceRead.model_validate(db_workspace)

    def get_workspace(self, workspace_id: uuid.UUID) -> Optional[WorkspaceRead]:
        """
        根据ID获取单个工作区

        Args:
            workspace_id: 工作区的UUID

        Returns:
            WorkspaceRead: 工作区读取模型，如果未找到则返回None
        """
        result = self.db.execute(select(Workspaces).where(Workspaces.id == workspace_id))
        workspace = result.scalar_one_or_none()
        if workspace:
            return WorkspaceRead.model_validate(workspace)
        return None

    def get_workspaces(self, skip: int = 0, limit: int = 100) -> List[WorkspaceRead]:
        """
        获取工作区列表，支持分页

        Args:
            skip: 跳过的记录数，默认为0
            limit: 返回的记录数限制，默认为100

        Returns:
            List[WorkspaceRead]: 工作区读取模型列表
        """
        result = self.db.execute(select(Workspaces).offset(skip).limit(limit))
        workspaces = result.scalars().all()
        return [WorkspaceRead.model_validate(ws) for ws in workspaces]

    def get_workspaces_by_owner(self, owner_id: uuid.UUID, skip: int, limit: int) -> List[WorkspaceRead]:
        """
        根据所有者ID获取工作区列表

        Args:
            owner_id: 所有者的用户ID

        Returns:
            List[WorkspaceRead]: 指定所有者的工作区读取模型列表
        """
        result = self.db.execute(select(Workspaces).where(Workspaces.owner_id == owner_id).offset(skip).limit(limit))
        workspaces = result.scalars().all()
        return [WorkspaceRead.model_validate(ws) for ws in workspaces]


    def get_joined_workspaces_by_user(self, user_id: uuid.UUID, skip: int, limit: int) -> List[WorkspaceRead]:
        """
        根据用户的ID获取用户加入的工作区列表
        Args:
            user_id: 用户的ID
        Returns:
            List[WorkspaceRead]: 用户加入的工作区读取模型列表
        """
        result = self.db.execute(select(Workspaces).join(WorkspaceUsers).where(WorkspaceUsers.user_id == user_id).offset(skip).limit(limit))
        workspaces = result.scalars().all()
        return [WorkspaceRead.model_validate(ws) for ws in workspaces]

    def update_workspace(self, workspace_id: uuid.UUID, workspace_update: WorkspaceUpdate) -> Optional[WorkspaceRead]:
        """
        更新工作区

        Args:
            workspace_id: 要更新的工作区UUID
            workspace_update: 包含更新字段的模型

        Returns:
            WorkspaceRead: 更新后的工作区读取模型，如果未找到则返回None
        """
        # 获取要更新的工作区
        result = self.db.execute(select(Workspaces).where(Workspaces.id == workspace_id))
        db_workspace = result.scalar_one_or_none()
        
        if not db_workspace:
            return None

        # 更新字段
        update_data = workspace_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_workspace, field, value)

        self.db.commit()
        self.db.refresh(db_workspace)
        return WorkspaceRead.model_validate(db_workspace)

    def delete_workspace(self, workspace_id: uuid.UUID) -> bool:
        """
        删除工作区

        Args:
            workspace_id: 要删除的工作区UUID

        Returns:
            bool: 删除成功返回True，否则返回False
        """
        result = self.db.execute(select(Workspaces).where(Workspaces.id == workspace_id))
        workspace = result.scalar_one_or_none()
        
        if not workspace:
            return False

        self.db.delete(workspace)
        self.db.commit()
        return True