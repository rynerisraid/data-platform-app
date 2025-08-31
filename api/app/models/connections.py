import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, Enum
import enum
from sqlalchemy.dialects.postgresql import UUID
from pydantic import BaseModel
from app.config.db import Base
import base64
from typing import Optional
from app.models.resources import Resources
# 连接器类型
class ConnectionType(str, enum.Enum):
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"


# DataConnectionCreate schema for creating new connections
class DataConnectionCreate(BaseModel):
    name: str
    db_type: ConnectionType
    host: str
    port: int
    database: str
    username: str
    password: str

    class Config:
        from_attributes = True


# DataConnectionTest schema for testing database connections
class DataConnectionTest(BaseModel):
    db_type: ConnectionType
    host: str
    port: int
    database: Optional[str] = None
    username: str
    password: str


    class Config:
        from_attributes = True

# DataConnectionTest schema for testing database connections
class DataConnectionTestResponse(BaseModel):
    success: bool
    error: Optional[str] = None
    message: Optional[str] = 'OK'


    class Config:
        from_attributes = True


# DataConnectionRead schema for reading connection information
class DataConnectionRead(BaseModel):
    id: uuid.UUID
    name: str
    db_type: ConnectionType
    host: str
    port: Optional[int] = None
    database: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None

    class Config:
        from_attributes = True


# 数据库连接模型
class DataBaseConnection(Resources):
    __tablename__ = "resources_database_connections"

    id = Column(UUID(as_uuid=True), ForeignKey('resources.id', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True, default=uuid.uuid4)
    db_type = Column(Enum(ConnectionType), name='database_type', nullable=False)
    host = Column(String, nullable=False)
    port = Column(Integer, nullable=True)
    database = Column(String, nullable=True)
    username = Column(String, nullable=True)
    # Store encrypted password for database connections
    password = Column(String, nullable=True)  # For database connections

    
    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return f'<DataConnection {self.name}>'
    

    # 多态配置
    __mapper_args__ = {
        "polymorphic_identity": "connector",  # 标识这是连接器类型
    }