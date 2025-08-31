"""
表数据查询服务测试用例

该模块包含对TableDataService的测试。
"""

import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock

from app.services.metadata import TableDataService
from app.models.metadata import QueryParams


@pytest.fixture
def mock_db():
    """模拟数据库会话"""
    return AsyncMock()


@pytest.fixture
def sample_user_id():
    """生成测试用户ID"""
    return uuid.uuid4()


@pytest.fixture
def sample_table_id():
    """生成测试表ID"""
    return uuid.uuid4()


@pytest.fixture
def sample_connection_id():
    """生成测试连接ID"""
    return uuid.uuid4()


@pytest.mark.asyncio
async def test_query_table_data(mock_db):
    """测试查询表数据"""
    # 准备测试数据
    table_name = "test_table"
    query_params = QueryParams(
        filters={"column1": "value1"},
        sort_by="column2",
        sort_order="asc",
        page=1,
        page_size=20
    )
    
    # 创建服务实例
    service = TableDataService(mock_db)
    
    # Mock metadata_service 的 get_metadata_table_by_name 方法
    mock_table_config = MagicMock()
    mock_table_config.database_name = "test_db"
    mock_table_config.table_name = "test_table"
    
    mock_column1 = MagicMock()
    mock_column1.column_name = "column1"
    mock_column2 = MagicMock()
    mock_column2.column_name = "column2"
    mock_table_config.columns = [mock_column1, mock_column2]
    
    service.metadata_service.get_metadata_table_by_name = AsyncMock(return_value=mock_table_config)
    
    # Mock execute 方法返回模拟数据
    mock_count_result = MagicMock()
    mock_count_result.scalar_one = MagicMock(return_value=100)
    
    mock_data_result = MagicMock()
    mock_row = MagicMock()
    mock_row.column1 = "value1"
    mock_row.column2 = "value2"
    mock_data_result.fetchall = MagicMock(return_value=[mock_row])
    
    mock_db.execute = AsyncMock(side_effect=[mock_count_result, mock_data_result])
    
    # 执行测试
    result = await service.query_table_data(table_name, query_params)
    
    # 验证结果
    assert result is not None
    assert "data" in result
    assert "total" in result
    assert "page" in result
    assert "page_size" in result
    assert "total_pages" in result
    service.metadata_service.get_metadata_table_by_name.assert_called_once_with(table_name)
    
    # 验证执行了两次数据库查询
    assert mock_db.execute.await_count == 2
    
    # 验证count查询
    count_query_call = mock_db.execute.call_args_list[0]
    assert "SELECT COUNT(*)" in str(count_query_call[0][0])
    assert "WHERE" in str(count_query_call[0][0])  # 验证包含WHERE条件
    assert "column1 = :param_1" in str(count_query_call[0][0])  # 验证过滤条件
    
    # 验证数据查询
    data_query_call = mock_db.execute.call_args_list[1]
    assert "SELECT" in str(data_query_call[0][0])
    assert "WHERE" in str(data_query_call[0][0])  # 验证包含WHERE条件
    assert "ORDER BY" in str(data_query_call[0][0])  # 验证排序条件
    assert "LIMIT" in str(data_query_call[0][0])  # 验证分页限制
    assert "OFFSET" in str(data_query_call[0][0])  # 验证偏移量


@pytest.mark.asyncio
async def test_query_table_data_table_not_found(mock_db):
    """测试查询表数据时表不存在"""
    # 准备测试数据
    table_name = "nonexistent_table"
    query_params = QueryParams()
    
    # 创建服务实例
    service = TableDataService(mock_db)
    
    # Mock metadata_service 的 get_metadata_table_by_name 方法返回None
    service.metadata_service.get_metadata_table_by_name = AsyncMock(return_value=None)
    
    # 执行测试并验证异常
    with pytest.raises(ValueError, match=f"Table configuration for '{table_name}' not found"):
        await service.query_table_data(table_name, query_params)
    
    service.metadata_service.get_metadata_table_by_name.assert_called_once_with(table_name)
"""
元数据模块测试用例

该模块包含对元数据表和字段操作的测试。
"""

import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock

from app.services.metadata import MetaDataTableService
from app.models.metadata import (
    MetaDataTableCreate, 
    MetaDataTableUpdate, 
    MetaDataTableColumnCreate, 
    MetaDataTableColumnUpdate,
)


@pytest.fixture
def mock_db():
    """模拟数据库会话"""
    return AsyncMock()


@pytest.fixture
def sample_user_id():
    """生成测试用户ID"""
    return uuid.uuid4()


@pytest.fixture
def sample_table_id():
    """生成测试表ID"""
    return uuid.uuid4()


@pytest.fixture
def sample_connection_id():
    """生成测试连接ID"""
    return uuid.uuid4()


@pytest.mark.asyncio
async def test_create_metadata_table(mock_db, sample_user_id, sample_connection_id):
    """测试创建元数据表"""
    # 准备测试数据
    table_data = MetaDataTableCreate(
        name="测试表",
        database_name="test_db",
        table_name="test_table",
        description="测试表描述",
        connection_id=sample_connection_id,
        display_name="测试表显示名"
    )
    
    # 创建服务实例
    service = MetaDataTableService(mock_db)
    
    # Mock resources_service 的 create_resource 方法
    mock_resource = MagicMock()
    mock_resource.id = uuid.uuid4()
    service.resources_service.create_resource = AsyncMock(return_value=mock_resource)
    
    # Mock add 和 commit 方法
    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()
    
    # 创建模拟的表对象
    mock_table = MagicMock()
    mock_table.id = mock_resource.id
    mock_table.database_name = "test_db"
    mock_table.table_name = "test_table"
    mock_table.description = "测试表描述"
    mock_table.connection_id = sample_connection_id
    mock_table.display_name = "测试表显示名"
    
    # Mock refresh 方法的行为
    mock_db.refresh.side_effect = lambda x: x.__dict__.update(mock_table.__dict__)
    
    # 执行测试
    result = await service.create_metadata_table(table_data, sample_user_id)
    
    # 验证结果
    assert result is not None
    assert result.database_name == table_data.database_name
    assert result.table_name == table_data.table_name
    assert result.connection_id == table_data.connection_id
    service.resources_service.create_resource.assert_called_once()
    mock_db.add.assert_called_once()
    mock_db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_metadata_table(mock_db, sample_table_id):
    """测试获取元数据表"""
    # 创建服务实例
    service = MetaDataTableService(mock_db)
    
    # 准备测试数据
    expected_table = MagicMock()
    expected_table.id = sample_table_id
    expected_table.database_name = "test_db"
    expected_table.table_name = "test_table"
    expected_table.columns = []
    
    # 创建模拟的查询结果
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = expected_table
    
    # 设置execute的返回值
    mock_db.execute.return_value = mock_result
    
    # 执行测试
    result = await service.get_metadata_table(sample_table_id)
    
    # 验证结果
    assert result is not None
    assert result.id == sample_table_id
    
    # 验证execute是否被正确调用
    assert mock_db.execute.called_once()
    
    # 验证查询是否正确
    query = mock_db.execute.call_args[0][0]
    assert str(query).startswith("SELECT metadata_table")  # 确保查询是针对metadata_table的
    assert query.whereclause is not None  # 确保有WHERE条件


@pytest.mark.asyncio
async def test_get_metadata_tables(mock_db, sample_table_id):
    """测试获取元数据表列表"""
    # 创建服务实例
    service = MetaDataTableService(mock_db)
    
    # Mock execute 方法返回模拟数据
    mock_table = MagicMock()
    mock_table.id = sample_table_id
    mock_table.database_name = "test_db"
    mock_table.table_name = "test_table"
    mock_table.columns = []
    
    mock_result = MagicMock()
    mock_result.scalars().all = MagicMock(return_value=[mock_table])
    mock_db.execute = AsyncMock(return_value=mock_result)
    
    # 执行测试
    result = await service.get_metadata_tables()
    
    # 验证结果
    assert len(result) == 1
    assert result[0].id == sample_table_id
    mock_db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_metadata_table(mock_db, sample_table_id):
    """测试更新元数据表"""
    # 准备测试数据
    table_update = MetaDataTableUpdate(
        display_name="更新后的显示名",
        description="更新后的描述"
    )
    
    # 创建服务实例
    service = MetaDataTableService(mock_db)
    
    # Mock execute 方法返回模拟数据
    mock_table = MagicMock()
    mock_table.id = sample_table_id
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=mock_table)
    mock_db.execute = AsyncMock(return_value=mock_result)
    
    # Mock resources_service 的 update_resource 方法
    service.resources_service.update_resource = AsyncMock()
    
    # Mock commit 和 refresh 方法
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()
    
    # 执行测试
    result = await service.update_metadata_table(sample_table_id, table_update)
    
    # 验证结果
    assert result is not None
    assert result.id == sample_table_id
    mock_db.execute.assert_awaited_once()
    mock_db.commit.assert_awaited_once()
    mock_db.refresh.assert_awaited_once_with(mock_table)


@pytest.mark.asyncio
async def test_delete_metadata_table(mock_db, sample_table_id):
    """测试删除元数据表"""
    # 创建服务实例
    service = MetaDataTableService(mock_db)
    
    # Mock resources_service 的 delete_resource 方法
    service.resources_service.delete_resource = AsyncMock(return_value=True)
    
    # 执行测试
    result = await service.delete_metadata_table(sample_table_id)
    
    # 验证结果
    assert result is True
    service.resources_service.delete_resource.assert_called_once_with(sample_table_id)


@pytest.mark.asyncio
async def test_create_table_column(mock_db, sample_table_id):
    """测试创建表字段"""
    # 准备测试数据
    column_data = MetaDataTableColumnCreate(
        column_name="test_column",
        data_type="varchar",
        ordinal_position=1,
        display_name="测试列",
        description="测试列描述"
    )
    
    # 创建服务实例
    service = MetaDataTableService(mock_db)
    
    # Mock add 和 commit 方法
    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()
    
    # 创建模拟的列对象并设置返回值
    mock_column = MagicMock()
    mock_column.seq = 1
    mock_column.table_id = sample_table_id
    mock_column.column_name = "test_column"
    mock_column.display_name = "测试列"
    mock_column.data_type = "varchar"
    mock_column.ordinal_position = 1
    mock_column.is_nullable = None
    mock_column.state = "A"
    mock_column.column_default = None
    mock_column.description = "测试列描述"
    
    # 当调用 refresh 时，将 mock_column 设置为 add 方法的参数
    def refresh_side_effect(obj):
        obj.__dict__.update(mock_column.__dict__)
        return obj
    mock_db.refresh.side_effect = refresh_side_effect
    
    # 执行测试
    result = await service.create_table_column(sample_table_id, column_data)
    
    # 验证结果
    assert result is not None
    mock_db.add.assert_called_once()
    mock_db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_table_columns(mock_db, sample_table_id):
    """测试获取表字段列表"""
    # 创建服务实例
    service = MetaDataTableService(mock_db)
    
    # Mock execute 方法返回模拟数据
    mock_column = MagicMock()
    mock_column.seq = 1
    mock_column.table_id = sample_table_id
    mock_column.column_name = "test_column"
    
    mock_result = MagicMock()
    mock_result.scalars().all = MagicMock(return_value=[mock_column])
    mock_db.execute = AsyncMock(return_value=mock_result)
    
    # 执行测试
    result = await service.get_table_columns(sample_table_id)
    
    # 验证结果
    assert len(result) == 1
    assert result[0].column_name == "test_column"
    mock_db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_table_column(mock_db):
    """测试更新表字段"""
    # 准备测试数据
    seq = 1
    column_update = MetaDataTableColumnUpdate(
        display_name="更新后的列名",
        description="更新后的描述"
    )
    
    # 创建服务实例
    service = MetaDataTableService(mock_db)
    
    # Mock execute 方法返回模拟数据
    mock_column = MagicMock()
    mock_column.seq = seq
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=mock_column)
    mock_db.execute = AsyncMock(return_value=mock_result)
    
    # Mock commit 和 refresh 方法
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()
    
    # 执行测试
    result = await service.update_table_column(seq, column_update)
    
    # 验证结果
    assert result is not None
    assert result.seq == seq
    mock_db.execute.assert_awaited_once()
    mock_db.commit.assert_awaited_once()
    mock_db.refresh.assert_awaited_once_with(mock_column)


@pytest.mark.asyncio
async def test_delete_table_column(mock_db):
    """测试删除表字段"""
    # 准备测试数据
    seq = 1
    
    # 创建服务实例
    service = MetaDataTableService(mock_db)
    
    # Mock execute 方法返回模拟数据
    mock_column = MagicMock()
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=mock_column)
    mock_db.execute = AsyncMock(return_value=mock_result)
    
    # Mock delete, commit 方法
    mock_db.delete = MagicMock()
    mock_db.commit = AsyncMock()
    
    # 执行测试
    result = await service.delete_table_column(seq)
    
    # 验证结果
    assert result is True
    mock_db.execute.assert_awaited_once()
    mock_db.delete.assert_called_once_with(mock_column)
    mock_db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_metadata_table_by_name(mock_db):
    """测试根据表名获取元数据表"""
    # 准备测试数据
    table_name = "test_table"
    
    # 创建服务实例
    service = MetaDataTableService(mock_db)
    
    # Mock execute 方法返回模拟数据
    mock_table = MagicMock()
    mock_table.id = uuid.uuid4()
    mock_table.table_name = table_name
    mock_table.database_name = "test_db"
    mock_table.columns = []
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=mock_table)
    mock_db.execute = AsyncMock(return_value=mock_result)
    
    # 执行测试
    result = await service.get_metadata_table_by_name(table_name)
    
    # 验证结果
    assert result is not None
    assert result.table_name == table_name
    mock_db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_metadata_table_by_name_not_found(mock_db):
    """测试根据表名获取元数据表但未找到"""
    # 准备测试数据
    table_name = "nonexistent_table"
    
    # 创建服务实例
    service = MetaDataTableService(mock_db)
    
    # Mock execute 方法返回None
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=None)
    mock_db.execute = AsyncMock(return_value=mock_result)
    
    # 执行测试
    result = await service.get_metadata_table_by_name(table_name)
    
    # 验证结果
    assert result is None
    mock_db.execute.assert_awaited_once()
