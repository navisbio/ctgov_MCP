import logging
from typing import Any
import mcp.types as types
from pydantic import AnyUrl
from .database import AACTDatabase
from .memo_manager import MemoManager
from .tools import ToolManager

logger = logging.getLogger('mcp_aact_server.handlers')

class MCPHandlers:
    def __init__(self, db: AACTDatabase):
        self.db = db
        self.memo_manager = MemoManager()
        self.tool_manager = ToolManager(db, self.memo_manager)

    async def handle_list_resources(self) -> list[types.Resource]:
        logger.debug("Handling list_resources request")
        return [
            types.Resource(
                uri=AnyUrl("memo://landscape"),
                name="Clinical Trial Landscape",
                description="Key findings about trial patterns, sponsor activity, and development trends",
                mimeType="text/plain",
            ),
            types.Resource(
                uri=AnyUrl("memo://metrics"),
                name="Trial Metrics",
                description="Quantitative metrics about trial phases, success rates, and temporal trends",
                mimeType="text/plain",
            )
        ]

    async def handle_read_resource(self, uri: AnyUrl) -> str:
        logger.debug(f"Handling read_resource request for URI: {uri}")
        if uri.scheme != "memo":
            logger.error(f"Unsupported URI scheme: {uri.scheme}")
            raise ValueError(f"Unsupported URI scheme: {uri.scheme}")

        path = str(uri).replace("memo://", "")
        if not path:
            logger.error("Empty resource path")
            raise ValueError("Empty resource path")

        if path == "insights":
            return self.memo_manager.get_insights_memo()
        elif path == "landscape":
            return self.memo_manager.get_landscape_memo()
        elif path == "metrics":
            return self.memo_manager.get_metrics_memo()
        else:
            logger.error(f"Unknown resource path: {path}")
            raise ValueError(f"Unknown resource path: {path}")

    async def handle_list_prompts(self) -> list[types.Prompt]:
        logger.debug("Handling list_prompts request")
        return [
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

    async def handle_get_prompt(self, name: str, arguments: dict[str, str] | None) -> types.GetPromptResult:
        from .prompts import PROMPT_TEMPLATE  # Import here to avoid circular dependency
        
        logger.debug(f"Handling get_prompt request for {name} with args {arguments}")
        if name != "indication-landscape":
            logger.error(f"Unknown prompt: {name}")
            raise ValueError(f"Unknown prompt: {name}")

        if not arguments or "topic" not in arguments:
            logger.error("Missing required argument: topic")
            raise ValueError("Missing required argument: topic")

        topic = arguments["topic"]
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

    async def handle_list_tools(self) -> list[types.Tool]:
        return self.tool_manager.get_available_tools()

    async def handle_call_tool(self, name: str, arguments: dict[str, Any] | None) -> list[types.TextContent]:
        return await self.tool_manager.execute_tool(name, arguments) 