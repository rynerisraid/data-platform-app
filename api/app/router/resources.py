from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select  # 添加select导入
from typing import List, Optional
import uuid

from app.config.db import get_async_db
from app.config.settings import settings  # 添加settings导入
from app.services.resources import ResourcesService
from app.services.connections import DataConnectionService  # 添加导入
from app.models.resources import ResourcesType, ResourcesState
from app.models.connections import (
    DataConnectionCreate,
    DataConnectionTest,
    DataConnectionRead,
    DataConnectionTestResponse,
    ConnectionType,
    DataBaseConnection
)
from app.utils.schema import BaseResponse
from app.models.auth import User,UserRead
from app.services.auth import get_current_user

# 创建router实例
router = APIRouter(dependencies=[Depends(get_current_user)])

# ------------------------------ 
# Resources 通用接口
# ------------------------------

@router.get("/")
async def read_resources(
    skip: int = 0,
    limit: int = 100,
    type: Optional[ResourcesType] = None,
    state: Optional[ResourcesState] = None,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取资源列表，支持分页和筛选
    """
    service = ResourcesService(db)
    resources = await service.get_resources(
        skip=skip,
        limit=limit,
        type=type,
        state=state,
        created_by=uuid.UUID(str(current_user.id))
    )
    return resources

@router.get("/{resource_id}")
async def read_resource(
    resource_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """
    根据ID获取单个资源
    """
    service = ResourcesService(db)
    resource = await service.get_resource(resource_id)
    if resource is None:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource

@router.put("/{resource_id}")
async def update_resource(
    resource_id: uuid.UUID,
    resource_update: dict,
    db: AsyncSession = Depends(get_async_db)
):
    """
    更新资源信息
    """
    service = ResourcesService(db)
    resource = await service.update_resource(resource_id, **resource_update)
    if resource is None:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource

@router.delete("/{resource_id}")
async def delete_resource(
    resource_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """
    删除资源（软删除）
    """
    service = ResourcesService(db)
    success = await service.delete_resource(resource_id)
    if not success:
        raise HTTPException(status_code=404, detail="Resource not found")
    return {"message": "Resource deleted successfully"}

# ------------------------------ 
# Connector 连接器相关接口
# ------------------------------

@router.post("/connectors/", response_model=BaseResponse[DataConnectionRead], status_code=status.HTTP_201_CREATED)
async def create_data_connection(
    data_connection: DataConnectionCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserRead = Depends(get_current_user)
):
    """
    创建新的数据连接器
    """
    # 生成资源ID
    resource_id = uuid.uuid4()
    print('创建新的数据连接器', resource_id, data_connection.name, current_user.id)

    # 先创建资源记录
    # resource_service = ResourcesService(db)
    # resources = await resource_service.create_resource(
    #     resource_id=resource_id,
    #     name=data_connection.name,
    #     type=ResourcesType.CONNECTOR,
    #     user_id=current_user.id,
    #     state=ResourcesState.PENDING
    # )

    # 使用 DataConnectionService 创建连接器
    connection_service = DataConnectionService(db)
    db_connection = await connection_service.create_data_connection(data_connection, id=resource_id)

    return BaseResponse[DataConnectionRead](data=db_connection)

@router.get("/connectors/", response_model=BaseResponse[List[DataConnectionRead]])
async def read_data_connections(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_db)
):
    """
    获取数据连接器列表
    """
    service = ResourcesService(db)
    connections = await service.get_resources_by_type(ResourcesType.CONNECTOR, skip, limit)
    # 需要将Resources对象转换为DataConnectionRead对象
    connection_reads = []
    for connection in connections:
        # 获取具体的连接器信息
        result = await db.execute(
            select(DataBaseConnection).where(DataBaseConnection.id == connection.id)
        )
        db_connection = result.scalar_one_or_none()
        if db_connection:
            connection_reads.append(DataConnectionRead.model_validate(db_connection))
    
    return BaseResponse[List[DataConnectionRead]](data=connection_reads)

@router.get("/connectors/{connection_id}", response_model=BaseResponse[DataConnectionRead])
async def read_data_connection(
    connection_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """
    根据ID获取单个数据连接器
    """
    service = ResourcesService(db)
    connection = await service.get_resource(connection_id)
    if connection is None or connection.type.value != ResourcesType.CONNECTOR.value:
        raise HTTPException(status_code=404, detail="Data connection not found")
    
    # 获取具体的连接器信息
    result = await db.execute(
        select(DataBaseConnection).where(DataBaseConnection.id == connection_id)
    )
    db_connection = result.scalar_one_or_none()
    if not db_connection:
        raise HTTPException(status_code=404, detail="Data connection not found")
    
    connection_read = DataConnectionRead.model_validate(db_connection)
    return BaseResponse[DataConnectionRead](data=connection_read)

@router.put("/connectors/{connection_id}", response_model=BaseResponse[DataConnectionRead])
async def update_data_connection(
    connection_id: uuid.UUID,
    connection_update: dict,
    db: AsyncSession = Depends(get_async_db)
):
    """
    更新数据连接器
    """
    service = ResourcesService(db)
    connection = await service.get_resource(connection_id)
    if connection is None or connection.type.value != ResourcesType.CONNECTOR.value:
        raise HTTPException(status_code=404, detail="Data connection not found")
    
    # 更新具体的连接器信息
    connection_service = DataConnectionService(db)
    updated_connection = await connection_service.update_data_connection(connection_id, connection_update)
    if updated_connection is None:
        raise HTTPException(status_code=404, detail="Data connection not found")
    
    return BaseResponse[DataConnectionRead](data=updated_connection)

@router.delete("/connectors/{connection_id}", response_model=BaseResponse[dict])
async def delete_data_connection(
    connection_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """
    删除数据连接器
    """
    service = ResourcesService(db)
    connection = await service.get_resource(connection_id)
    if connection is None or connection.type.value != ResourcesType.CONNECTOR.value:
        raise HTTPException(status_code=404, detail="Data connection not found")
    
    # 删除具体的连接器实例
    connection_service = DataConnectionService(db)
    success = await connection_service.delete_data_connection(connection_id)
    if not success:
        raise HTTPException(status_code=404, detail="Data connection not found")
    
    # 软删除资源记录
    success = await service.delete_resource(connection_id)
    if not success:
        raise HTTPException(status_code=404, detail="Data connection not found")
    
    return BaseResponse[dict](data={"message": "Data connection deleted successfully"})

# 测试数据库连接
@router.post("/connectors/test/", response_model=BaseResponse[DataConnectionTestResponse])
async def test_data_connection(
    connection_config: DataConnectionTest,
    db: AsyncSession = Depends(get_async_db)  # 添加数据库依赖
):
    """
    测试数据库连接
    """
    try:
        import asyncpg
        import aiomysql
        from motor.motor_asyncio import AsyncIOMotorClient
        
        if connection_config.db_type == ConnectionType.POSTGRESQL:
            # 测试 PostgreSQL 连接
            conn = await asyncpg.connect(
                host=connection_config.host,
                port=connection_config.port,
                user=connection_config.username,
                password=connection_config.password,
                database=connection_config.database
            )
            await conn.close()
            return BaseResponse[DataConnectionTestResponse](data=DataConnectionTestResponse(success=True))

        elif connection_config.db_type == ConnectionType.MYSQL:
            # 测试 MySQL 连接
            conn = await aiomysql.connect(
                host=connection_config.host,
                port=connection_config.port,
                user=connection_config.username,
                password=connection_config.password,
                db=connection_config.database
            )
            conn.close()
            return BaseResponse[DataConnectionTestResponse](data=DataConnectionTestResponse(success=True))

        elif connection_config.db_type == ConnectionType.MONGODB:
            # 测试 MongoDB 连接
            connection_string = f"mongodb://{connection_config.username}:{connection_config.password}@{connection_config.host}:{connection_config.port}"
            client = AsyncIOMotorClient(connection_string)
            await client.admin.command('ping')
            client.close()
            return BaseResponse[DataConnectionTestResponse](data=DataConnectionTestResponse(success=True))

        else:
            return BaseResponse[DataConnectionTestResponse](
                data=DataConnectionTestResponse(
                    success=False, 
                    error="Unsupported database type"
                )
            )

    except Exception as e:
        # 连接失败，返回 False
        return BaseResponse[DataConnectionTestResponse](
            data=DataConnectionTestResponse(
                success=False, 
                error=str(e)
            )
        )

# ------------------------------ 
# Metadata 元数据相关接口
# ------------------------------

@router.post("/metadata/", status_code=status.HTTP_201_CREATED)
async def create_metadata(
    metadata_data: dict,  # TODO: 需要定义具体的元数据模型
    db: AsyncSession = Depends(get_async_db),
    current_user: UserRead = Depends(get_current_user)
):
    """
    创建新的元数据
    """
    service = ResourcesService(db)
    metadata = await service.create_resource(
        name=metadata_data.get("name", "Unnamed Metadata"),
        type=ResourcesType.METADATA,
        user_id=current_user.id,
        state=ResourcesState.PENDING
    )
    return metadata

@router.get("/metadata/", response_model=List[dict])
async def read_metadata_list(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_db)
):
    """
    获取元数据列表
    """
    service = ResourcesService(db)
    metadata_list = await service.get_resources_by_type(ResourcesType.METADATA, skip, limit)
    return metadata_list

@router.get("/metadata/{metadata_id}")
async def read_metadata(
    metadata_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """
    根据ID获取单个元数据
    """
    service = ResourcesService(db)
    metadata = await service.get_resource(metadata_id)
    if metadata is None or metadata.type.value != ResourcesType.METADATA.value:
        raise HTTPException(status_code=404, detail="Metadata not found")
    return metadata

@router.put("/metadata/{metadata_id}")
async def update_metadata(
    metadata_id: uuid.UUID,
    metadata_update: dict,
    db: AsyncSession = Depends(get_async_db)
):
    """
    更新元数据
    """
    service = ResourcesService(db)
    metadata = await service.update_resource(metadata_id, **metadata_update)
    if metadata is None or metadata.type.value != ResourcesType.METADATA.value:
        raise HTTPException(status_code=404, detail="Metadata not found")
    return metadata

@router.delete("/metadata/{metadata_id}")
async def delete_metadata(
    metadata_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """
    删除元数据
    """
    service = ResourcesService(db)
    metadata = await service.get_resource(metadata_id)
    if metadata is None or metadata.type.value != ResourcesType.METADATA.value:
        raise HTTPException(status_code=404, detail="Metadata not found")
    
    success = await service.delete_resource(metadata_id)
    if not success:
        raise HTTPException(status_code=404, detail="Metadata not found")
    return {"message": "Metadata deleted successfully"}