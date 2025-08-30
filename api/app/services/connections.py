import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete, update
from app.models.connections import DataBaseConnection, ConnectionType, DataConnectionCreate, DataConnectionRead
from app.config.settings import settings

class DataConnectionService:
    """
    数据连接服务类，提供对数据连接的完整CRUD操作
    遵循单一职责原则，专门处理数据连接相关业务逻辑
    """
    def __init__(self, db: AsyncSession):
        """
        初始化数据连接服务
        
        Args:
            db: 异步数据库会话实例
        """
        self.db = db

    async def create_data_connection(self, data_connection: DataConnectionCreate, id: Optional[uuid.UUID] = None) -> DataConnectionRead:
        """
        创建新的数据连接记录

        Args:
            data_connection: 数据连接创建模型，包含要创建的数据连接信息
            id: 可选的连接器ID，默认为None将自动生成

        Returns:
            DataConnectionRead: 创建后的数据连接读取模型
        """
        # 处理密码加密
        db_data_connection = DataBaseConnection(
            id=id,
            db_type=data_connection.db_type,
            host=data_connection.host,
            port=data_connection.port,
            database=data_connection.database,
            username=data_connection.username
        )
        if data_connection.password:
            db_data_connection.set_encrypted_password(
                data_connection.password, 
                settings.DATASOURCE_KEY
            )
        
        self.db.add(db_data_connection)
        await self.db.commit()
        await self.db.refresh(db_data_connection)
        return DataConnectionRead.model_validate(db_data_connection)

    async def get_data_connection(self, connection_id: uuid.UUID) -> Optional[DataConnectionRead]:
        """
        根据ID获取单个数据连接记录
        
        Args:
            connection_id: 数据连接的UUID
            
        Returns:
            DataConnectionRead: 数据连接读取模型，如果未找到则返回None
        """
        result = await self.db.execute(
            select(DataBaseConnection).where(DataBaseConnection.id == connection_id)
        )
        data_connection = result.scalar_one_or_none()
        if data_connection:
            return DataConnectionRead.model_validate(data_connection)
        return None

    async def get_data_connections(self, skip: int = 0, limit: int = 100) -> List[DataConnectionRead]:
        """
        获取数据连接列表，支持分页
        
        Args:
            skip: 跳过的记录数，默认为0
            limit: 返回的记录数限制，默认为100
            
        Returns:
            List[DataConnectionRead]: 数据连接读取模型列表
        """
        result = await self.db.execute(
            select(DataBaseConnection).offset(skip).limit(limit)
        )
        data_connections = result.scalars().all()
        return [DataConnectionRead.model_validate(dc) for dc in data_connections]

    async def update_data_connection(self, connection_id: uuid.UUID, connection_update: dict) -> Optional[DataConnectionRead]:
        """
        更新数据连接记录
        
        Args:
            connection_id: 要更新的数据连接UUID
            connection_update: 包含更新字段的字典
            
        Returns:
            DataConnectionRead: 更新后的数据连接读取模型，如果未找到则返回None
        """
        stmt = (
            update(DataBaseConnection)
            .where(DataBaseConnection.id == connection_id)
            .values(**connection_update)
        )
        await self.db.execute(stmt)
        await self.db.commit()
        
        # 获取更新后的记录
        result = await self.db.execute(
            select(DataBaseConnection).where(DataBaseConnection.id == connection_id)
        )
        updated_data_connection = result.scalar_one_or_none()
        if updated_data_connection:
            return DataConnectionRead.model_validate(updated_data_connection)
        return None

    async def delete_data_connection(self, connection_id: uuid.UUID) -> bool:
        """
        删除数据连接记录
        
        Args:
            connection_id: 要删除的数据连接UUID
            
        Returns:
            bool: 删除成功返回True，否则返回False
        """
        stmt = delete(DataBaseConnection).where(DataBaseConnection.id == connection_id)
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0

    # Additional utility methods
    async def get_data_connections_by_type(self, connection_type: ConnectionType) -> List[DataConnectionRead]:
        """
        根据连接类型获取数据连接列表
        
        Args:
            connection_type: 连接类型枚举值
            
        Returns:
            List[DataConnectionRead]: 指定类型的数据连接读取模型列表
        """
        result = await self.db.execute(
            select(DataBaseConnection).where(DataBaseConnection.type == connection_type)
        )
        data_connections = result.scalars().all()
        return [DataConnectionRead.model_validate(dc) for dc in data_connections]

    async def get_active_data_connections(self) -> List[DataConnectionRead]:
        """
        获取所有激活状态的数据连接
        
        Returns:
            List[DataConnectionRead]: 激活状态的数据连接读取模型列表
        """
        result = await self.db.execute(
            select(DataBaseConnection).where(DataBaseConnection.is_active == True)
        )
        data_connections = result.scalars().all()
        return [DataConnectionRead.model_validate(dc) for dc in data_connections]

    async def test_connection(self, connection_config: DataConnectionCreate) -> bool:
        """
        根据配置测试数据库链接配置是否生效
        
        Args:
            connection_config: 数据连接配置对象，包含连接信息
            
        Returns:
            bool: 连接成功返回True，失败返回False
        """
        try:
            # 获取实际的枚举值进行比较
            connection_type = connection_config.db_type.value if hasattr(connection_config.db_type, 'value') else str(connection_config.db_type)
            
            if connection_type == ConnectionType.POSTGRESQL.value:
                import asyncpg
                # 直接使用传入的密码
                conn = await asyncpg.connect(
                    host=connection_config.host,
                    port=connection_config.port,
                    user=connection_config.username,
                    password=connection_config.password,
                    database=connection_config.database
                )
                await conn.close()
                return True
                
            elif connection_type == ConnectionType.MYSQL.value:
                # 为避免导入错误，使用延迟导入
                try:
                    import aiomysql
                    # 直接使用传入的密码
                    conn = await aiomysql.connect(
                        host=connection_config.host,
                        port=connection_config.port,
                        user=connection_config.username,
                        password=connection_config.password,
                        db=connection_config.database
                    )
                    await conn.ensure_closed()
                    return True
                except ImportError:
                    # 如果没有安装aiomysql，返回False表示连接测试失败
                    return False
                
            # 其他类型的数据源可以在这里添加处理逻辑
            # 对于API等非数据库类型，可以添加相应的测试逻辑
            else:
                return False
        except Exception as e:
            # 连接失败
            return False