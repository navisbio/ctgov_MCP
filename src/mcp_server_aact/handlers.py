import logging
from typing import Any
import mcp.types as types
from pydantic import AnyUrl
from mcp_server_aact.database import AACTDatabase
from mcp_server_aact.memo_manager import MemoManager
from mcp_server_aact.tools import ToolManager
import json
from mcp_server_aact.resources import get_resources
from mcp_server_aact.errors import ResourceError, handle_errors

logger = logging.getLogger('mcp_aact_server.handlers')

class MCPHandlers:
    def __init__(self, db: AACTDatabase, schema: dict):
        self.db = db
        self.schema = schema
        self.memo_manager = MemoManager()
        self.tool_manager = ToolManager(db, self.memo_manager)
        logger.info("MCPHandlers initialized")

    @handle_errors(ResourceError, "Error listing resources: {error}")
    async def handle_list_resources(self) -> list[types.Resource]:
        logger.debug("Handling list_resources request")
        resources = get_resources()
        logger.debug(f"Returning {len(resources)} resources")
        return resources

    @handle_errors(ResourceError, "Error reading resource {uri}: {error}")
    async def handle_read_resource(self, uri: AnyUrl) -> str:
        logger.info(f"Handling read_resource request for URI: {uri}")
        
        scheme = uri.scheme
        if scheme not in ["memo", "schema"]:
            raise ResourceError(f"Unsupported URI scheme: {scheme}")

        if scheme == "schema":
            path = str(uri).replace("schema://", "")
            if path == "database":
                return json.dumps(self.schema, indent=2)
            else:
                raise ResourceError(f"Unknown schema resource: {path}")
            
        path = str(uri).replace("memo://", "")
        if not path:
            raise ResourceError("Empty resource path")

        logger.debug(f"Reading resource for path: {path}")
        if path == "insights":
            return self.memo_manager.get_insights_memo()
        else:
            raise ResourceError(f"Unknown resource path: {path}")

    @handle_errors(ResourceError, "Error listing prompts: {error}")
    async def handle_list_prompts(self) -> list[types.Prompt]:
        logger.debug("Handling list_prompts request")
        prompts = [
            types.Prompt(
                name="indication-landscape",
                description="Analyzes clinical trial patterns, development trends, and competitive dynamics within specific therapeutic areas",
                arguments=[
                    types.PromptArgument(
                        name="topic",
                        description="Therapeutic area or indication to analyze (e.g., 'multiple sclerosis', 'breast cancer')",
                        required=True,
                    )
                ],
            )
        ]
        logger.debug(f"Returning {len(prompts)} prompts")
        return prompts

    @handle_errors(ResourceError, "Error getting prompt {name}: {error}")
    async def handle_get_prompt(self, name: str, arguments: dict[str, str] | None) -> types.GetPromptResult:
        logger.info(f"Handling get_prompt request for {name} with args {arguments}")
        
        from .prompts import PROMPT_TEMPLATE
        
        if name != "indication-landscape":
            raise ResourceError(f"Unknown prompt: {name}")

        if not arguments or "topic" not in arguments:
            raise ResourceError("Missing required argument: topic")

        topic = arguments["topic"]
        logger.debug(f"Generating prompt for topic: {topic}")
        prompt = PROMPT_TEMPLATE.format(topic=topic)

        return types.GetPromptResult(
            description=f"Clinical trial landscape analysis for {topic}",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(type="text", text=prompt.strip()),
                )
            ],
        )

    @handle_errors(ResourceError, "Error listing tools: {error}")
    async def handle_list_tools(self) -> list[types.Tool]:
        logger.debug("Handling list_tools request")
        return self.tool_manager.get_available_tools()

    @handle_errors(ResourceError, "Error calling tool {name}: {error}")
    async def handle_call_tool(self, name: str, arguments: dict[str, Any] | None) -> list[types.TextContent]:
        """Handle tool execution requests"""
        logger.info(f"Handling call_tool request for {name}")
        return await self.tool_manager.execute_tool(name, arguments)