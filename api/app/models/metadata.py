'''
 MetaDataTable 继承自 Resources
 1) 表格信息管理 MetaDataTable

 2) 表格字段管理 MetaDataTableColumn


'''

import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy import Column, String, Integer, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID,BIGINT,ENUM
from sqlalchemy.orm import relationship
from app.config.db import Base
from app.models.resources import Resources,STATE_ENUM
from pydantic import BaseModel
from app.models.resources import ResourcesType, ResourcesState


class MetaDataTable(Resources):
    __tablename__ = "resources_metadata_tables"

    id = Column(UUID(as_uuid=True), ForeignKey('resources.id', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True, default=uuid.uuid4)
    database_name = Column(String(255), nullable=False)
    table_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    connection_id = Column(UUID(as_uuid=True), ForeignKey('resources_database_connections.id'), nullable=False)
    display_name = Column(String(255), nullable=True)
    
    # 关联字段
    columns = relationship("MetaDataTableColumn", back_populates="table", cascade="all, delete-orphan")
    
    __mapper_args__ = {
        "polymorphic_identity": "metadata",
    }


class MetaDataTableColumn(Base):
    __tablename__ = "resources_metadata_table_columns"

    seq = Column(BIGINT, primary_key=True, autoincrement=True)
    table_id = Column(UUID(as_uuid=True), ForeignKey('resources_metadata_tables.id'), nullable=False)
    column_name = Column(String(255), nullable=False)
    display_name = Column(String(255), nullable=True)
    data_type = Column(String(100), nullable=False)
    ordinal_position = Column(Integer, nullable=False)
    is_nullable = Column(String(10), nullable=True)
    state = Column(STATE_ENUM, default='A')  # e.g., A, P
    column_default = Column(Text, nullable=True)
    description = Column(Text, nullable=True)

    
    # 关联表
    table = relationship("MetaDataTable", back_populates="columns")
    

# Pydantic models for API requests and responses
class MetaDataTableCreate(BaseModel):
    """创建元数据表的请求模型"""
    name: str  # 资源名称
    database_name: str
    table_name: str
    description: Optional[str] = None
    connection_id: uuid.UUID
    display_name: Optional[str] = None


class MetaDataTableUpdate(BaseModel):
    """更新元数据表的请求模型"""
    name: Optional[str] = None
    database_name: Optional[str] = None
    table_name: Optional[str] = None
    description: Optional[str] = None
    connection_id: Optional[uuid.UUID] = None
    display_name: Optional[str] = None
    state: Optional[ResourcesState] = None


class MetaDataTableRead(BaseModel):
    """元数据表的响应模型"""
    id: uuid.UUID
    name: str
    database_name: str
    table_name: str
    description: Optional[str] = None
    connection_id: uuid.UUID
    display_name: Optional[str] = None
    type: ResourcesType
    state: ResourcesState
    created_by: uuid.UUID


class MetaDataTableColumnCreate(BaseModel):
    """创建元数据表字段的请求模型"""
    column_name: str
    display_name: Optional[str] = None
    data_type: str
    ordinal_position: int
    is_nullable: Optional[str] = None
    column_default: Optional[str] = None
    description: Optional[str] = None


class MetaDataTableColumnUpdate(BaseModel):
    """更新元数据表字段的请求模型"""
    column_name: Optional[str] = None
    display_name: Optional[str] = None
    data_type: Optional[str] = None
    ordinal_position: Optional[int] = None
    is_nullable: Optional[str] = None
    column_default: Optional[str] = None
    description: Optional[str] = None
    state: Optional[str] = None


class MetaDataTableColumnRead(MetaDataTableColumnCreate):
    """元数据表字段的响应模型"""
    seq: int
    table_id: uuid.UUID
    state: str


class MetaDataTableWithColumnsRead(MetaDataTableRead):
    """包含字段信息的元数据表响应模型"""
    columns: List[MetaDataTableColumnRead] = []


# 数据查询相关模型
class QueryParams(BaseModel):
    """查询参数模型"""
    filters: Optional[Dict[str, Any]] = None
    sort_by: Optional[str] = None
    sort_order: Optional[str] = "asc"  # "asc" or "desc"
    page: int = 1
    page_size: int = 20
    select_fields: Optional[List[str]] = None


class TableDataResponse(BaseModel):
    """表格数据查询响应模型"""
    data: List[Dict[str, Any]]
    total: int
    page: int
    page_size: int
    total_pages: int