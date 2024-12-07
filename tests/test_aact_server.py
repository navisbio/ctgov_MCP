import pytest
import os
from unittest.mock import patch, Mock
from datetime import datetime
import json
from pydantic import AnyUrl
import mcp.types as types

from mcp_server_aact.database import AACTDatabase
from mcp_server_aact.server import main
from mcp_server_aact.handlers import MCPHandlers

# Set up test environment
os.environ["DB_USER"] = "test_user"
os.environ["DB_PASSWORD"] = "test_password"

@pytest.fixture
def mock_db():
    with patch('mcp_server_aact.database.AACTDatabase') as MockClass:
        # Create instance mock
        instance = MockClass.return_value
        
        # Setup default return values
        instance.execute_query.return_value = [
            {
                "nct_id": "NCT00000000",
                "brief_title": "Test Study",
                "phase": "Phase 1"
            }
        ]
        instance.get_insights_memo.return_value = "Test memo content"
        
        yield instance

@pytest.fixture
def handlers(mock_db):
    return MCPHandlers(mock_db)

@pytest.mark.asyncio
async def test_list_resources(handlers):
    resources = await handlers.handle_list_resources()
    assert len(resources) == 1
    assert resources[0].name == "Business Insights Memo"
    assert resources[0].mimeType == "text/plain"

@pytest.mark.asyncio
async def test_read_resource(handlers, mock_db):
    response = await handlers.handle_read_resource(AnyUrl("memo://insights"))
    assert response == "Test memo content"
    mock_db.get_insights_memo.assert_called_once()

@pytest.mark.asyncio
async def test_list_tools(handlers):
    tools = await handlers.handle_list_tools()
    assert len(tools) == 4  # read-query, list-tables, describe-table, append-insight
    
    tool_names = {tool.name for tool in tools}
    assert tool_names == {"read-query", "list-tables", "describe-table", "append-insight"}

@pytest.mark.asyncio
async def test_call_tool_list_tables(handlers, mock_db):
    mock_db.execute_query.return_value = [
        {"table_name": "studies"},
        {"table_name": "conditions"}
    ]
    
    response = await handlers.handle_call_tool("list-tables", {})
    mock_db.execute_query.assert_called_once()
    
    # Convert response to string for assertion
    response_text = response[0].text
    assert "studies" in response_text
    assert "conditions" in response_text

@pytest.mark.asyncio
async def test_call_tool_read_query(handlers, mock_db):
    query = "SELECT * FROM ctgov.studies LIMIT 1"
    response = await handlers.handle_call_tool("read-query", {"query": query})
    
    mock_db.execute_query.assert_called_once_with(query)
    response_text = response[0].text
    assert "NCT00000000" in response_text

@pytest.mark.asyncio
async def test_call_tool_append_insight(handlers, mock_db):
    insight = "Test insight"
    response = await handlers.handle_call_tool("append-insight", {"insight": insight})
    
    mock_db.add_insight.assert_called_once_with(insight)
    response_text = response[0].text
    assert "Insight added to memo" in response_text

@pytest.mark.asyncio
async def test_invalid_tool(handlers):
    with pytest.raises(ValueError, match="Unknown tool"):
        await handlers.handle_call_tool("invalid-tool", {})

@pytest.mark.asyncio
async def test_invalid_query(handlers, mock_db):
    with pytest.raises(ValueError, match="Only SELECT queries are allowed"):
        await handlers.handle_call_tool("read-query", {"query": "INSERT INTO table"}) 