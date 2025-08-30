"""
Resources 服务模块

该模块用于管理和操作 Resources（资源），Resources 是一个基表，支持多种类型的资源:
1) 连接器 (connector)
2) 计算节点 (compute_node)
3) 元数据 (metadata)

Service 层负责处理与 Resources 相关的业务逻辑，包括创建、查询、更新、删除各种类型的资源，
以及提供资源状态管理等功能。

主要功能包括：
- 创建和初始化新的资源
- 查询和管理现有资源
- 更新资源信息和状态
- 删除资源
- 根据资源类型和状态进行筛选查询
- 提供资源与用户关联的操作支持
"""

import uuid
from typing import List, Optional
from app.config.db import AsyncSession
from sqlalchemy import select
from app.models.resources import Resources, ResourcesType, ResourcesState


class ResourcesService:
    """
    Resources服务类，提供对各种资源的完整CRUD操作
    """

    def __init__(self, db: AsyncSession):
        """
        初始化Resources服务

        Args:
            db: 数据库会话实例
        """
        self.db = db

    async def create_resource(self, name: str, type: ResourcesType, user_id: uuid.UUID, 
                       state: ResourcesState = ResourcesState.PENDING, 
                       resource_id: Optional[uuid.UUID] = None) -> Resources:
        """
        创建新的资源

        Args:
            name: 资源名称
            type: 资源类型 (连接器/计算节点/元数据)
            created_by: 创建者用户ID
            state: 资源状态，默认为待激活状态
            id: 资源ID，可选参数，默认为None，将自动生成

        Returns:
            Resources: 创建后的资源对象
        """
        print('create resource', name, state, user_id)
        db_resource = Resources(
            id=resource_id,
            name=name,
            type=ResourcesType.CONNECTOR,
            state= ResourcesState.PENDING,
            created_by=user_id,
        )
        self.db.add(db_resource)
        await self.db.commit()
        return db_resource

    async def get_resource(self, resource_id: uuid.UUID) -> Optional[Resources]:
        """
        根据ID获取单个资源

        Args:
            resource_id: 资源的UUID

        Returns:
            Resources: 资源对象，如果未找到则返回None
        """
        result = await self.db.execute(select(Resources).where(Resources.id == resource_id))
        resource = result.scalar_one_or_none()
        return resource

    async def get_resources(self, skip: int = 0, limit: int = 100, 
                      type: Optional[ResourcesType] = None,
                      state: Optional[ResourcesState] = None,
                      created_by: Optional[uuid.UUID] = None) -> List[Resources]:
        """
        获取资源列表，支持分页和筛选

        Args:
            skip: 跳过的记录数，默认为0
            limit: 返回的记录数限制，默认为100
            type: 资源类型筛选条件（可选）
            state: 资源状态筛选条件（可选）
            created_by: 创建者ID筛选条件（可选）

        Returns:
            List[Resources]: 资源对象列表
        """
        query = select(Resources)
        
        if type:
            query = query.where(Resources.type == type)
            
        if state:
            query = query.where(Resources.state == state)
            
        if created_by:
            query = query.where(Resources.created_by == created_by)
            
        result = await self.db.execute(query.offset(skip).limit(limit))
        resources = result.scalars().all()
        return list(resources)

    async def update_resource(self, resource_id: uuid.UUID, **kwargs) -> Optional[Resources]:
        """
        更新资源信息

        Args:
            resource_id: 要更新的资源UUID
            **kwargs: 要更新的字段和值

        Returns:
            Resources: 更新后的资源对象，如果未找到则返回None
        """
        result = await self.db.execute(select(Resources).where(Resources.id == resource_id))
        db_resource = result.scalar_one_or_none()
        
        if not db_resource:
            return None

        # 更新字段
        for field, value in kwargs.items():
            if hasattr(db_resource, field) and field != 'id':
                setattr(db_resource, field, value)

        await self.db.commit()
        await self.db.refresh(db_resource)
        return db_resource

    async def delete_resource(self, resource_id: uuid.UUID) -> bool:
        """
        删除资源（软删除，将状态设置为DELETED）

        Args:
            resource_id: 要删除的资源UUID

        Returns:
            bool: 删除成功返回True，否则返回False
        """
        result = await self.update_resource(resource_id, state=ResourcesState.DELETED)
        return result is not None

    async def get_resources_by_type(self, type: ResourcesType, skip: int = 0, 
                              limit: int = 100) -> List[Resources]:
        """
        根据资源类型获取资源列表

        Args:
            type: 资源类型
            skip: 跳过的记录数，默认为0
            limit: 返回的记录数限制，默认为100

        Returns:
            List[Resources]: 指定类型的资源对象列表
        """
        result = await self.db.execute(
            select(Resources)
            .where(Resources.type == type)
            .offset(skip)
            .limit(limit)
        )
        resources = result.scalars().all()
        return list(resources)

    async def get_resources_by_creator(self, created_by: uuid.UUID, skip: int = 0, 
                                 limit: int = 100) -> List[Resources]:
        """
        根据创建者获取资源列表

        Args:
            created_by: 创建者的用户ID
            skip: 跳过的记录数，默认为0
            limit: 返回的记录数限制，默认为100

        Returns:
            List[Resources]: 指定创建者的资源对象列表
        """
        result = await self.db.execute(
            select(Resources)
            .where(Resources.created_by == created_by)
            .offset(skip)
            .limit(limit)
        )
        resources = result.scalars().all()
        return list(resources)