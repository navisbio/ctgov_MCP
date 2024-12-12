import pytest
from unittest.mock import Mock
from mcp_server_aact.tools import ToolManager
from mcp.types import TextContent, Tool

@pytest.fixture
def mock_db():
    mock = Mock()
    mock.execute_query.return_value = [{"result": "test"}]
    return mock

@pytest.fixture
def mock_memo_manager():
    return Mock()

@pytest.fixture
def tool_manager(mock_db, mock_memo_manager):
    return ToolManager(mock_db, mock_memo_manager)

async def test_get_available_tools(tool_manager):
    tools = tool_manager.get_available_tools()
    assert len(tools) > 0
    assert all(isinstance(t, Tool) for t in tools)
    tool_names = {t.name for t in tools}
    assert "read-query" in tool_names
    assert "list-tables" in tool_names
    assert "describe-table" in tool_names

async def test_execute_tool_read_query(tool_manager, mock_db):
    query = "SELECT * FROM studies"
    result = await tool_manager.execute_tool("read-query", {"query": query})
    mock_db.execute_query.assert_called_once_with(query)
    assert isinstance(result[0], TextContent)

async def test_execute_tool_invalid_query(tool_manager):
    with pytest.raises(ValueError, match="Only SELECT queries are allowed"):
        await tool_manager.execute_tool("read-query", {"query": "DELETE FROM studies"})

async def test_execute_tool_list_tables(tool_manager, mock_db):
    result = await tool_manager.execute_tool("list-tables", None)
    mock_db.execute_query.assert_called_once()
    assert "table_schema = 'ctgov'" in mock_db.execute_query.call_args[0][0]
    assert isinstance(result[0], TextContent)

async def test_execute_tool_describe_table(tool_manager, mock_db):
    result = await tool_manager.execute_tool("describe-table", {"table_name": "studies"})
    mock_db.execute_query.assert_called_once()
    assert "table_name = %s" in mock_db.execute_query.call_args[0][0]
    assert isinstance(result[0], TextContent)

async def test_execute_tool_append_insights(tool_manager, mock_memo_manager):
    finding = "New finding"
    result = await tool_manager.execute_tool("append-insight", {"finding": finding})
    mock_memo_manager.add_insights.assert_called_once_with(finding)
    assert isinstance(result[0], TextContent)
    assert "Insight added" in result[0].text 