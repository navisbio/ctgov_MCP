import pytest
from unittest.mock import Mock, AsyncMock
from mcp_server_aact.database import AACTDatabase
from mcp_server_aact.handlers import MCPHandlers
from mcp_server_aact.memo_manager import MemoManager
from mcp_server_aact.tools import ToolManager
from mcp.types import Resource, Tool, Prompt, GetPromptResult, PromptMessage, TextContent
from pydantic import AnyUrl

@pytest.fixture
def mock_db():
    mock = Mock(spec=AACTDatabase)
    # Set up mock responses
    mock.execute_query.return_value = [
        {"table_name": "studies"},
        {"table_name": "conditions"}
    ]
    return mock

@pytest.fixture
def memo_manager():
    return MemoManager()

@pytest.fixture
def tool_manager(mock_db, memo_manager):
    return ToolManager(mock_db, memo_manager)

@pytest.fixture
def handlers(mock_db, memo_manager, tool_manager):
    return MCPHandlers(mock_db, schema={})

async def test_list_resources(handlers):
    resources = await handlers.handle_list_resources()
    assert len(resources) == 2
    assert all(isinstance(r, Resource) for r in resources)
    
    # Get resource names for easier testing
    resource_names = {r.name for r in resources}
    assert "Insights on Clinical Trial Landscape" in resource_names
    assert "AACT Database Schema" in resource_names

async def test_call_tool_list_tables(handlers, mock_db):
    result = await handlers.handle_call_tool("list-tables", None)
    
    # Verify the mock was called correctly
    mock_db.execute_query.assert_called_once()
    assert "table_schema = 'ctgov'" in mock_db.execute_query.call_args[0][0]
    
    # Verify the result
    assert isinstance(result, list)
    assert len(result) > 0
    assert all(isinstance(r, TextContent) for r in result)
    assert "studies" in result[0].text
    assert "conditions" in result[0].text

async def test_read_resource(handlers):
    uri = AnyUrl("memo://insights")
    result = await handlers.handle_read_resource(uri)
    assert isinstance(result, str)
    assert "No landscape analysis available yet" in result

async def test_read_resource_invalid_scheme(handlers):
    uri = AnyUrl("http://example.com")
    with pytest.raises(ValueError):
        await handlers.handle_read_resource(uri)

async def test_list_prompts(handlers):
    prompts = await handlers.handle_list_prompts()
    assert len(prompts) == 1
    assert all(isinstance(p, Prompt) for p in prompts)
    assert prompts[0].name == "indication-landscape"

async def test_get_prompt(handlers):
    name = "indication-landscape"
    args = {"topic": "multiple sclerosis"}
    result = await handlers.handle_get_prompt(name, args)
    assert isinstance(result, GetPromptResult)
    assert "multiple sclerosis" in result.description
    assert len(result.messages) == 1
    assert isinstance(result.messages[0], PromptMessage)

async def test_get_prompt_invalid_name(handlers):
    with pytest.raises(ValueError):
        await handlers.handle_get_prompt("invalid", {"topic": "test"})

async def test_get_prompt_missing_args(handlers):
    with pytest.raises(ValueError):
        await handlers.handle_get_prompt("indication-landscape", None)

async def test_list_tools(handlers):
    tools = await handlers.handle_list_tools()
    assert len(tools) > 0
    assert all(isinstance(t, Tool) for t in tools)
    assert any(t.name == "read-query" for t in tools)
    assert any(t.name == "list-tables" for t in tools)

async def test_call_tool_invalid_name(handlers):
    with pytest.raises(ValueError):
        await handlers.handle_call_tool("invalid", None)

async def test_call_tool_missing_args(handlers):
    with pytest.raises(ValueError):
        await handlers.handle_call_tool("read-query", None) 