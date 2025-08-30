'''
 MetaDataTable 继承自 Resources
 1) 表格信息管理 MetaDataTable

 2) 表格字段管理 MetaDataTableColumn


'''

import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID,BIGINT,ENUM
from sqlalchemy.orm import relationship
from app.config.db import Base
from app.models.resources import Resources,STATE_ENUM


class MetaDataTable(Resources):
    __tablename__ = "resources_metadata_tables"

    id = Column(UUID(as_uuid=True), ForeignKey('resources.id', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True, default=uuid.uuid4)
    database_name = Column(String(255), nullable=False)
    table_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    connection_id = Column(UUID(as_uuid=True), ForeignKey('resources_database_connections.id'), nullable=False)
    
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
    data_type = Column(String(100), nullable=False)
    ordinal_position = Column(Integer, nullable=False)
    is_nullable = Column(String(10), nullable=True)
    state = Column(STATE_ENUM, default='A')  # e.g., A, P
    column_default = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    
    # 关联表
    table = relationship("MetaDataTable", back_populates="columns")
    