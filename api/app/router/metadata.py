"""
元数据路由模块

该模块提供元数据表和字段的RESTful API接口。

主要接口包括：
- 创建、查询、更新、删除元数据表
- 创建、查询、更新、删除元数据表字段
- 根据元数据配置查询实际表数据
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid

from app.config.db import get_async_db
from app.models.resources import ResourcesType
from app.services.metadata import MetaDataTableService
from app.services.tabledata import TableDataService
from app.models.metadata import (
    MetaDataTableCreate, 
    MetaDataTableRead, 
    MetaDataTableUpdate,
    MetaDataTableColumnCreate, 
    MetaDataTableColumnRead, 
    MetaDataTableColumnUpdate,
    MetaDataTableWithColumnsRead,
    QueryParams,
    TableDataResponse
)
from app.models.auth import UserRead
from app.services.auth import get_current_user
from app.utils.schema import BaseResponse

# 创建路由实例，所有路径都以 /metadata 为前缀
router = APIRouter(prefix="/metadata", dependencies=[Depends(get_current_user)])


@router.post("/", response_model=BaseResponse[MetaDataTableRead], status_code=status.HTTP_201_CREATED)
async def create_metadata_table(
    table_data: MetaDataTableCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserRead = Depends(get_current_user)
):
    """
    创建元数据表
    
    Args:
        table_data: 元数据表创建信息（包括字段信息）
        db: 数据库会话依赖
        current_user: 当前登录用户信息
        
    Returns:
        BaseResponse[MetaDataTableRead]: 创建的元数据表信息
    """
    service = MetaDataTableService(db)
    resource_id = uuid.uuid4()  # 生成新的资源ID
    try:
        # 创建元数据表
        db_table = await service.create_metadata_table(resource_id, table_data, current_user.id)

        # 如果提供了字段信息，则同时创建字段
        if table_data.columns:
            for column_data in table_data.columns:
                await service.create_table_column(db_table.id, column_data)
            
            # 重新获取包含字段的表信息
            db_table = await service.get_metadata_table(db_table.id)
        
        table_read = MetaDataTableRead.model_validate(db_table)
        return BaseResponse[MetaDataTableRead](data=table_read)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{table_id}", response_model=BaseResponse[MetaDataTableWithColumnsRead])
async def read_metadata_table(
    table_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """
    获取元数据表详情（包含字段信息）
    
    Args:
        table_id: 元数据表ID
        db: 数据库会话依赖
        
    Returns:
        BaseResponse[MetaDataTableWithColumnsRead]: 元数据表详细信息
    """
    service = MetaDataTableService(db)
    db_table = await service.get_metadata_table(table_id)
    if not db_table:
        raise HTTPException(status_code=404, detail="Metadata table not found")
    
    columns_read = [
        MetaDataTableColumnRead(
            seq=column.seq,
            table_id=column.table_id,
            column_name=column.column_name,
            display_name=column.display_name,
            data_type=column.data_type,
            ordinal_position=column.ordinal_position,
            is_nullable=column.is_nullable,
            state=column.state,
            column_default=column.column_default,
            description=column.description
        )
        for column in db_table.columns
    ]

    table_read = MetaDataTableWithColumnsRead.model_validate(columns_read)

    return BaseResponse[MetaDataTableWithColumnsRead](data=table_read)


@router.get("/", response_model=BaseResponse[List[MetaDataTableRead]])
async def list_metadata_tables(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_db)
):
    """
    获取元数据表列表
    
    Args:
        skip: 跳过的记录数，默认为0
        limit: 返回的记录数限制，默认为100
        db: 数据库会话依赖
        
    Returns:
        BaseResponse[List[MetaDataTableRead]]: 元数据表列表
    """
    service = MetaDataTableService(db)
    tables = await service.get_metadata_tables(skip, limit)
    
    tables_read = [
        MetaDataTableRead.model_validate(table)
        for table in tables
    ]
    
    return BaseResponse[List[MetaDataTableRead]](data=tables_read)


@router.put("/{table_id}", response_model=BaseResponse[MetaDataTableRead])
async def update_metadata_table(
    table_id: uuid.UUID,
    table_update: MetaDataTableUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    """
    更新元数据表
    
    Args:
        table_id: 元数据表ID
        table_update: 元数据表更新信息
        db: 数据库会话依赖
        
    Returns:
        BaseResponse[MetaDataTableRead]: 更新后的元数据表信息
    """
    service = MetaDataTableService(db)
    db_table = await service.update_metadata_table(table_id, table_update)
    if not db_table:
        raise HTTPException(status_code=404, detail="Metadata table not found")
    
    table_read = MetaDataTableRead.model_validate(db_table)
    
    return BaseResponse[MetaDataTableRead](data=table_read)


@router.delete("/{table_id}", response_model=BaseResponse[dict])
async def delete_metadata_table(
    table_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """
    删除元数据表（软删除）
    
    Args:
        table_id: 元数据表ID
        db: 数据库会话依赖
        
    Returns:
        BaseResponse[dict]: 删除结果信息
    """
    service = MetaDataTableService(db)
    success = await service.delete_metadata_table(table_id)
    if not success:
        raise HTTPException(status_code=404, detail="Metadata table not found")
    
    return BaseResponse[dict](data={"message": "Metadata table deleted successfully"})


# 字段相关接口
@router.post("/{table_id}/columns/", response_model=BaseResponse[MetaDataTableColumnRead], status_code=status.HTTP_201_CREATED)
async def create_table_column(
    table_id: uuid.UUID,
    column_data: MetaDataTableColumnCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """
    为元数据表添加字段
    
    Args:
        table_id: 元数据表ID
        column_data: 字段创建信息
        db: 数据库会话依赖
        
    Returns:
        BaseResponse[MetaDataTableColumnRead]: 创建的字段信息
    """
    service = MetaDataTableService(db)
    # 检查表是否存在
    table = await service.get_metadata_table(table_id)
    if not table:
        raise HTTPException(status_code=404, detail="Metadata table not found")
    
    try:
        db_column = await service.create_table_column(table_id, column_data)
        column_read = MetaDataTableColumnRead.model_validate(db_column)
        return BaseResponse[MetaDataTableColumnRead](data=column_read)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{table_id}/columns/", response_model=BaseResponse[List[MetaDataTableColumnRead]])
async def list_table_columns(
    table_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """
    获取元数据表的所有字段
    
    Args:
        table_id: 元数据表ID
        db: 数据库会话依赖
        
    Returns:
        BaseResponse[List[MetaDataTableColumnRead]]: 字段列表
    """
    service = MetaDataTableService(db)
    # 检查表是否存在
    table = await service.get_metadata_table(table_id)
    if not table:
        raise HTTPException(status_code=404, detail="Metadata table not found")
    
    columns = await service.get_table_columns(table_id)
    columns_read = [
        MetaDataTableColumnRead(
            seq=column.seq,
            table_id=column.table_id,
            column_name=column.column_name,
            display_name=column.display_name,
            data_type=column.data_type,
            ordinal_position=column.ordinal_position,
            is_nullable=column.is_nullable,
            state=column.state,
            column_default=column.column_default,
            description=column.description
        )
        for column in columns
    ]
    
    return BaseResponse[List[MetaDataTableColumnRead]](data=columns_read)


@router.put("/columns/{seq}", response_model=BaseResponse[MetaDataTableColumnRead])
async def update_table_column(
    seq: int,
    column_update: MetaDataTableColumnUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    """
    更新元数据表字段
    
    Args:
        seq: 字段序列号
        column_update: 字段更新信息
        db: 数据库会话依赖
        
    Returns:
        BaseResponse[MetaDataTableColumnRead]: 更新后的字段信息
    """
    service = MetaDataTableService(db)
    db_column = await service.update_table_column(seq, column_update)
    if not db_column:
        raise HTTPException(status_code=404, detail="Metadata table column not found")
    
    column_read = MetaDataTableColumnRead(
        seq=db_column.seq,
        table_id=db_column.table_id,
        column_name=db_column.column_name,
        display_name=db_column.display_name,
        data_type=db_column.data_type,
        ordinal_position=db_column.ordinal_position,
        is_nullable=db_column.is_nullable,
        state=db_column.state,
        column_default=db_column.column_default,
        description=db_column.description
    )
    
    return BaseResponse[MetaDataTableColumnRead](data=column_read)


@router.delete("/columns/{seq}", response_model=BaseResponse[dict])
async def delete_table_column(
    seq: int,
    db: AsyncSession = Depends(get_async_db)
):
    """
    删除元数据表字段
    
    Args:
        seq: 字段序列号
        db: 数据库会话依赖
        
    Returns:
        BaseResponse[dict]: 删除结果信息
    """
    service = MetaDataTableService(db)
    success = await service.delete_table_column(seq)
    if not success:
        raise HTTPException(status_code=404, detail="Metadata table column not found")
    
    return BaseResponse[dict](data={"message": "Metadata table column deleted successfully"})


# 数据查询接口
@router.post("/{table_name}/query", response_model=BaseResponse[TableDataResponse])
async def query_table_data(
    table_name: str,
    query_params: QueryParams,
    db: AsyncSession = Depends(get_async_db)
):
    """
    根据配置查询表格数据
    
    Args:
        table_name: 表名
        query_params: 查询参数
        db: 数据库会话依赖
        
    Returns:
        BaseResponse[TableDataResponse]: 查询结果
    """
    try:
        service = TableDataService(db)
        result = await service.query_table_data(table_name, query_params)
        return BaseResponse[TableDataResponse](data=TableDataResponse(**result))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))