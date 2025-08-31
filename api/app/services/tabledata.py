"""
表数据服务模块

该模块提供基于元数据配置的数据查询功能。
"""

from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.models.metadata import QueryParams
from app.services.metadata import MetaDataTableService


class TableDataService:
    """
    表数据服务类，提供基于元数据配置的数据查询功能
    """

    def __init__(self, db: AsyncSession):
        """
        初始化表数据服务

        Args:
            db: 数据库会话实例
        """
        self.db = db
        self.metadata_service = MetaDataTableService(db)

    async def query_table_data(
        self, 
        table_name: str, 
        query_params: QueryParams
    ) -> Dict[str, Any]:
        """
        根据元数据配置查询表格数据

        Args:
            table_name: 表名
            query_params: 查询参数

        Returns:
            Dict[str, Any]: 查询结果，包括数据、总数、分页信息等
        """
        # 获取表配置
        table_config = await self.metadata_service.get_metadata_table_by_name(table_name)
        if not table_config:
            raise ValueError(f"Table configuration for '{table_name}' not found")
        
        table_config_columns = await self.metadata_service.get_table_columns(table_config.id)
        
        # 构建查询SQL
        # 注意：这是一个示例实现，实际项目中应该根据具体的数据连接来查询
        # 这里只是演示如何根据元数据配置来构建查询
        
        # 构建SELECT子句
        if query_params.select_fields:
            # 验证选择的字段是否在元数据中存在
            valid_columns = {col.column_name for col in table_config_columns}
            selected_columns = [field for field in query_params.select_fields if field in valid_columns]
            if not selected_columns:
                selected_columns = [col.column_name for col in table_config_columns]
        else:
            selected_columns = [col.column_name for col in table_config_columns]
        
        select_clause = ", ".join(selected_columns)
        
        # 构建FROM子句
        from_clause = f"{table_config.database_name}.{table_config.table_name}"
        
        # 构建WHERE子句
        where_conditions = []
        params = {}
        if query_params.filters:
            for field, value in query_params.filters.items():
                # 验证字段是否在元数据中存在
                if field in {col.column_name for col in table_config_columns}:
                    where_conditions.append(f"{field} = :{field}")
                    params[field] = value
        
        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)
        
        # 构建ORDER BY子句
        order_clause = ""
        if query_params.sort_order and query_params.sort_by and query_params.sort_by in {col.column_name for col in table_config_columns}:
            sort_order = "ASC" if query_params.sort_order.lower() == "asc" else "DESC"
            order_clause = f"ORDER BY {query_params.sort_by} {sort_order}"
        
        # 构建LIMIT和OFFSET子句
        limit_clause = f"LIMIT {query_params.page_size}"
        offset_clause = f"OFFSET {(query_params.page - 1) * query_params.page_size}"
        
        # 构建完整的查询SQL
        count_sql = f"SELECT COUNT(*) FROM {from_clause} {where_clause}"
        data_sql = f"SELECT {select_clause} FROM {from_clause} {where_clause} {order_clause} {limit_clause} {offset_clause}"
        
        # 执行COUNT查询
        count_result = await self.db.execute(text(count_sql), params)
        total = count_result.scalar_one()
        
        # 执行数据查询
        data_result = await self.db.execute(text(data_sql), params)
        rows = data_result.fetchall()
        
        # 将结果转换为字典列表
        data = []
        for row in rows:
            row_dict = {}
            for i, column_name in enumerate(selected_columns):
                row_dict[column_name] = getattr(row, column_name, None)
            data.append(row_dict)
        
        # 计算总页数
        total_pages = (total + query_params.page_size - 1) // query_params.page_size if query_params.page_size > 0 else 0
        
        return {
            "data": data,
            "total": total,
            "page": query_params.page,
            "page_size": query_params.page_size,
            "total_pages": total_pages
        }