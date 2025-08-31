"""
元数据服务模块

该模块用于管理和操作元数据资源，包括元数据表和表字段的管理。

主要功能包括：
- 创建、查询、更新、删除元数据表
- 创建、查询、更新、删除元数据表字段
- 提供元数据表与字段的关联操作支持
"""

import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.metadata import (
    MetaDataTable, 
    MetaDataTableColumn,
    MetaDataTableColumnRead,
    MetaDataTableCreate,
    MetaDataTableRead,
    MetaDataTableUpdate,
    MetaDataTableColumnCreate,
    MetaDataTableColumnUpdate
)
from app.models.connections import DataBaseConnection, DataConnectionRead
from app.services.resources import ResourcesService


class MetaDataTableService:
    """
    元数据表服务类，提供对元数据表和字段的完整CRUD操作
    """

    def __init__(self, db: AsyncSession):
        """
        初始化元数据表服务

        Args:
            db: 数据库会话实例
        """
        self.db = db
        self.resources_service = ResourcesService(db)
        self.connection_sessions = None  # 假设有一个连接服务类，用于管理数据库连接

    async def create_metadata_table(self, 
                                    resource_id: Optional[uuid.UUID],
                                    table_data: MetaDataTableCreate, 
                                    user_id: uuid.UUID) -> MetaDataTableRead:
        """
        创建新的元数据表

        Args:
            table_data: 元数据表创建信息
            user_id: 创建者用户ID

        Returns:
            MetaDataTable: 创建后的元数据表对象
        """
        # 先创建资源，
        # resource = await self.resources_service.create_resource(
        #     name=table_data.name,
        #     type=ResourcesType.METADATA,
        #     user_id=user_id,
        #     state=ResourcesState.ACTIVE
        # )
        
        #这个框架会自动处理资源的创建和关联

        # 创建元数据表记录
        db_table = MetaDataTable(
            id=resource_id,
            database_name=table_data.database_name,
            table_name=table_data.table_name,
            description=table_data.description,
            connection_id=table_data.connection_id,
            display_name=table_data.display_name,
            user_id=user_id,
        )
        
        self.db.add(db_table)
        await self.db.commit()
        await self.db.refresh(db_table)
        return MetaDataTableRead.model_validate(db_table)

    async def get_metadata_table(self, table_id: uuid.UUID) -> Optional[MetaDataTable]:
        """
        根据ID获取单个元数据表（包含字段信息）

        Args:
            table_id: 元数据表的UUID

        Returns:
            MetaDataTable: 元数据表对象，如果未找到则返回None
        """
        result = await self.db.execute(
            select(MetaDataTable)
            .options(selectinload(MetaDataTable.columns))
            .where(MetaDataTable.id == table_id)
        )
        return result.scalar_one_or_none()

    async def get_metadata_table_by_name(self, table_name: str) -> Optional[MetaDataTableRead]:
        """
        根据表名获取元数据表（包含字段信息）

        Args:
            table_name: 元数据表名

        Returns:
            MetaDataTable: 元数据表对象，如果未找到则返回None
        """
        result = await self.db.execute(
            select(MetaDataTable)
            .options(selectinload(MetaDataTable.columns))
            .where(MetaDataTable.table_name == table_name)
        )
        return MetaDataTableRead.model_validate(result.scalar_one_or_none())

    async def get_metadata_tables(self, skip: int = 0, limit: int = 100) -> List[MetaDataTableRead]:
        """
        获取元数据表列表

        Args:
            skip: 跳过的记录数，默认为0
            limit: 返回的记录数限制，默认为100

        Returns:
            List[MetaDataTable]: 元数据表对象列表
        """
        result = await self.db.execute(
            select(MetaDataTable)
            .options(selectinload(MetaDataTable.columns))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def update_metadata_table(self, table_id: uuid.UUID, table_update: MetaDataTableUpdate) -> Optional[MetaDataTable]:
        """
        更新元数据表信息

        Args:
            table_id: 要更新的元数据表UUID
            table_update: 更新信息

        Returns:
            MetaDataTable: 更新后的元数据表对象，如果未找到则返回None
        """
        # 更新资源信息
        update_fields = {}
        if table_update.name is not None:
            update_fields["name"] = table_update.name
        if table_update.state is not None:
            update_fields["state"] = table_update.state
            
        if update_fields:
            await self.resources_service.update_resource(table_id, **update_fields)
        
        # 更新元数据表信息
        result = await self.db.execute(
            select(MetaDataTable).where(MetaDataTable.id == table_id)
        )
        db_table = result.scalar_one_or_none()
        if not db_table:
            return None
        
        # 更新字段
        update_data = table_update.dict(exclude_unset=True)
        # 移除资源相关字段
        update_data.pop("name", None)
        update_data.pop("state", None)
        
        for key, value in update_data.items():
            setattr(db_table, key, value)
        
        await self.db.commit()
        await self.db.refresh(db_table)
        return db_table

    async def delete_metadata_table(self, table_id: uuid.UUID) -> bool:
        """
        删除元数据表（软删除，将资源状态设置为DELETED）

        Args:
            table_id: 要删除的元数据表UUID

        Returns:
            bool: 删除成功返回True，否则返回False
        """
        # 软删除资源
        success = await self.resources_service.delete_resource(table_id)
        return success

    async def create_table_column(self, table_id: uuid.UUID, column_data: MetaDataTableColumnCreate) -> MetaDataTableColumn:
        """
        为元数据表添加字段

        Args:
            table_id: 元数据表UUID
            column_data: 字段创建信息

        Returns:
            MetaDataTableColumn: 创建后的字段对象
        """
        db_column = MetaDataTableColumn(
            table_id=table_id,
            column_name=column_data.column_name,
            display_name=column_data.display_name,
            data_type=column_data.data_type,
            ordinal_position=column_data.ordinal_position,
            is_nullable=column_data.is_nullable,
            column_default=column_data.column_default,
            description=column_data.description
        )
        self.db.add(db_column)
        await self.db.commit()
        await self.db.refresh(db_column)
        return db_column

    async def get_table_columns(self, table_id: uuid.UUID) -> List[MetaDataTableColumnRead]:
        """
        获取元数据表的所有字段

        Args:
            table_id: 元数据表UUID

        Returns:
            List[MetaDataTableColumn]: 字段对象列表
        """
        db_columns = await self.db.execute(
            select(MetaDataTableColumn)
            .where(MetaDataTableColumn.table_id == table_id)
            .order_by(MetaDataTableColumn.ordinal_position)
        )

        return [MetaDataTableColumnRead.model_validate(col) for col in db_columns]
    
    
    async def get_table_columns_info_by_(self, 
                                         connection_id: Optional[uuid.UUID], 
                                         table_name: Optional[str], 
                                         schema_name: Optional[str], 
                                         database_name: Optional[str]):
        """
        根据数据库的原始信息读取字段
        
        Args:
            table_name
            schema_name: 针对Postgresql
            database_name:

        """
        db_connections = await self.db.execute(
            select(DataBaseConnection).where(DataBaseConnection.id == connection_id)
        )
        db_config: DataConnectionRead = db_connections.scalar_one_or_none()
        if not db_config:
            return None
        
        # 根据连接类型创建相应数据库引擎
        engine = None
        try:
            if db_config.db_type == "postgresql":
                from sqlalchemy import create_engine
                connection_url = f"postgresql://{db_config.username}:{db_config.password}@{db_config.host}:{db_config.port}/{database_name or db_config.database_name}"
                engine = create_engine(connection_url)
            elif db_config.db_type == "mysql":
                from sqlalchemy import create_engine
                connection_url = f"mysql+pymysql://{db_config.username}:{db_config.password}@{db_config.host}:{db_config.port}/{database_name or db_config.database_name}"
                engine = create_engine(connection_url)
            # 可以根据需要添加其他数据库类型支持
            
            if not engine:
                raise ValueError(f"Unsupported database type: {db_config.db_type}")
                
            # 查询表的字段信息
            with engine.connect() as conn:
                from sqlalchemy import text
                
                # 构建查询字段信息的SQL语句
                if db_config.db_type == "postgresql":
                    sql = """
                        SELECT 
                            column_name,
                            data_type,
                            ordinal_position,
                            is_nullable,
                            column_default
                        FROM information_schema.columns 
                        WHERE table_name = :table_name
                        AND table_schema = :schema_name
                        ORDER BY ordinal_position
                    """
                    schema = schema_name or 'public'
                else:  # mysql等其他数据库
                    sql = """
                        SELECT 
                            column_name,
                            data_type,
                            ordinal_position,
                            is_nullable,
                            column_default
                        FROM information_schema.columns 
                        WHERE table_name = :table_name
                        AND table_schema = :database_name
                        ORDER BY ordinal_position
                    """
                    schema = database_name or db_config.database_name
                    
                result = conn.execute(text(sql), {
                    "table_name": table_name,
                    "schema_name": schema,
                    "database_name": schema
                })
                
                # 将查询结果转换为字段创建模型
                columns = []
                for row in result:
                    column = MetaDataTableColumnCreate(
                        column_name=row.column_name,
                        data_type=row.data_type,
                        ordinal_position=row.ordinal_position,
                        is_nullable=row.is_nullable,
                        column_default=row.column_default
                    )
                    columns.append(column)
                    
                return columns
                
        except Exception as e:
            # 处理连接或查询异常
            print(f"Error connecting to database or querying columns: {str(e)}")
            return None
        finally:
            # 关闭引擎连接
            if engine:
                engine.dispose()
    async def update_table_column(self, seq: int, column_update: MetaDataTableColumnUpdate) -> Optional[MetaDataTableColumnRead]:
        """
        更新元数据表字段信息

        Args:
            seq: 字段序列号
            column_update: 更新信息

        Returns:
            MetaDataTableColumn: 更新后的字段对象，如果未找到则返回None
        """
        result = await self.db.execute(
            select(MetaDataTableColumn).where(MetaDataTableColumn.seq == seq)
        )
        db_column = result.scalar_one_or_none()
        if not db_column:
            return None
        
        update_data = column_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_column, key, value)
        
        await self.db.commit()
        await self.db.refresh(db_column)
        return MetaDataTableColumnRead.model_validate(db_column)
    

    async def delete_table_column(self, seq: int) -> bool:
        """
        删除元数据表字段

        Args:
            seq: 要删除的字段序列号

        Returns:
            bool: 删除成功返回True，否则返回False
        """
        result = await self.db.execute(
            select(MetaDataTableColumn).where(MetaDataTableColumn.seq == seq)
        )
        db_column = result.scalar_one_or_none()
        if not db_column:
            return False
        
        await self.db.delete(db_column)
        await self.db.commit()
        return True
    