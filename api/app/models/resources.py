"""
 Resources 为基表
 子类：
 1)连接器 connector
 2)计算节点 compute_node
 3)元数据  metadata

"""

import uuid
from sqlalchemy import Column, String, DateTime, Integer, Boolean, Text, ForeignKey, Enum
import enum
from sqlalchemy.dialects.postgresql import UUID
import datetime
from app.config.db import Base


# 资源类型
class ResourcesType(str, enum.Enum):
    CONNECTOR = "connector"
    COMPUTE_NODE = "compute_node"
    METADATA = "metadata"


# 资源状态
class ResourcesState(str, enum.Enum):
    ACTIVE = "A"    # 可用
    PENDING = "P"   # 待激活
    DELETED = "D"   # 删除


# 资源模型
class Resources(Base):
    __tablename__ = "resources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    type = Column(Enum(ResourcesType), nullable=False)
    state = Column(Enum(ResourcesState), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)


    __mapper_args__ = {
        "polymorphic_on": type # 指定了多态表哪个字段区分该条记录是属于哪个继承表
    }


# Define the ENUM separately to prevent Alembic from creating it multiple times
STATE_ENUM = Enum("A", "P", "D", name="state_enum")