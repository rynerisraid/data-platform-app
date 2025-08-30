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

    def set_encrypted_password(self, password: str, encryption_key: Optional[str] = None):
        """
        Encrypt and store the password for database connections.
        If encryption_key is provided, store an encrypted version for database connections.
        """
        if password and encryption_key:
            try:
                # Simple XOR encryption with key - for demonstration purposes
                # In production, you should use a proper encryption library
                key_bytes = encryption_key.encode('utf-8')
                password_bytes = password.encode('utf-8')
                encrypted_bytes = bytearray()
                
                for i in range(len(password_bytes)):
                    encrypted_bytes.append(password_bytes[i] ^ key_bytes[i % len(key_bytes)])
                
                self.password = base64.b64encode(encrypted_bytes).decode('utf-8')
            except Exception:
                # If encryption fails, store as None
                self.password = None
        else:
            self.password = None

    def get_decrypted_password(self, encryption_key: str) -> str | None:
        """
        Decrypt and return the original password for connecting to other databases.
        This requires an encryption key to decrypt the stored password.
        """
        if self.password is None or encryption_key is None:
            return None
        
        try:
            # Simple XOR decryption with key
            key_bytes = encryption_key.encode('utf-8')
            encrypted_bytes = base64.b64decode(self.password.encode('utf-8'))
            decrypted_bytes = bytearray()
            
            for i in range(len(encrypted_bytes)):
                decrypted_bytes.append(encrypted_bytes[i] ^ key_bytes[i % len(key_bytes)])
            
            return decrypted_bytes.decode('utf-8')
        except Exception:
            # If decryption fails, return None
            return None

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return f'<DataConnection {self.name}>'
    

    # 多态配置
    __mapper_args__ = {
        "polymorphic_identity": "connector",  # 标识这是连接器类型
    }