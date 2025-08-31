'''
归属Workspace的数据报表目录

可能保存如下的数据：

菜单：
    -数据报表
     - 报表1
     - 目录
        - 报表2
        ... 
    -数据集市
    -数据资产
    -数据模型
'''

import uuid
import enum
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import datetime
from app.config.db import Base
from app.models.resources import Resources, ResourcesType, ResourcesState
from app.models.workspace import Workspaces
from app.models.auth import User

# 目录项类型
class CatalogItemType(str, enum.Enum):
    REPORT = "report"
    FOLDER = "folder"
    DATAMART = "datamart"
    ASSET = "asset"
    MODEL = "model"


class CatalogItem(Base):
    __tablename__ = "catalog_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    type = Column(String, nullable=False)  # 使用CatalogItemType枚举
    workspace_id = Column(UUID(as_uuid=True), ForeignKey('workspaces.id'), nullable=False)
    parent_id = Column(UUID(as_uuid=True), ForeignKey('catalog_items.id'), nullable=True)
    resource_id = Column(UUID(as_uuid=True), ForeignKey('resources.id'), nullable=True)
    order = Column(Integer, default=0)  # 排序字段
    is_active = Column(Boolean, default=True)  # 是否激活状态
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    
    # 关系定义
    workspace = relationship("Workspaces", backref="catalog_items")
    parent = relationship("CatalogItem", remote_side=[id], backref="children")
    resource = relationship("Resources", backref="catalog_items")
    creator = relationship("User", backref="created_catalog_items")
    
    def __repr__(self):
        return f'<CatalogItem {self.name}>'


# 如果需要将目录项作为资源类型
class CatalogResource(Resources):
    __tablename__ = "catalog_resources"
    
    id = Column(UUID(as_uuid=True), ForeignKey('resources.id'), primary_key=True)
    catalog_item_id = Column(UUID(as_uuid=True), ForeignKey('catalog_items.id'), nullable=False)
    
    __mapper_args__ = {
        "polymorphic_identity": "catalog",
    }
    
    def __repr__(self):
        return f'<CatalogResource {self.id}>'