import logging
from typing import Any
import mcp.types as types
from pydantic import AnyUrl
from .database import AACTDatabase

logger = logging.getLogger('mcp_aact_server.handlers')

class MCPHandlers:
    def __init__(self, db: AACTDatabase):
        self.db = db

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
            return self.db.get_insights_memo()
        elif path == "landscape":
            return self.db.get_landscape_memo()
        elif path == "metrics":
            return self.db.get_metrics_memo()
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
        return [
            types.Tool(
                name="read-query",
                description="Execute a SELECT query on the AACT clinical trials database",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "SELECT SQL query to execute"},
                    },
                    "required": ["query"],
                },
            ),
            types.Tool(
                name="list-tables",
                description="List all tables in the AACT database",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
            types.Tool(
                name="describe-table",
                description="Get the schema information for a specific table in AACT",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {"type": "string", "description": "Name of the table to describe"},
                    },
                    "required": ["table_name"],
                },
            ),
            types.Tool(
                name="append-insight",
                description="Add a business insight to the memo",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "insight": {"type": "string", "description": "Business insight discovered from data analysis"},
                    },
                    "required": ["insight"],
                },
            ),
            types.Tool(
                name="append-landscape",
                description="Add findings about trial patterns and development trends",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "finding": {"type": "string", "description": "Analysis finding about trial patterns or trends"},
                    },
                    "required": ["finding"],
                },
            ),
            types.Tool(
                name="append-metrics",
                description="Add quantitative metrics about trials",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "metric": {"type": "string", "description": "Quantitative metric or statistical finding"},
                    },
                    "required": ["metric"],
                },
            ),
        ]

    async def handle_call_tool(self, name: str, arguments: dict[str, Any] | None) -> list[types.TextContent]:
        try:
            # Update the tool name check
            if name not in {"list-tables", "describe-table", "read-query", "append-insight", 
                           "append-landscape", "append-metrics"}:
                raise ValueError(f"Unknown tool: {name}")

            # Then check for arguments
            if not arguments and name != "list-tables":  # list-tables doesn't need arguments
                raise ValueError("Missing arguments")

            if name == "list-tables":
                results = self.db.execute_query("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'ctgov'
                    ORDER BY table_name;
                """)
                return [types.TextContent(type="text", text=str(results))]

            elif name == "describe-table":
                if "table_name" not in arguments:
                    raise ValueError("Missing table_name argument")
                results = self.db.execute_query("""
                    SELECT column_name, data_type, character_maximum_length
                    FROM information_schema.columns
                    WHERE table_schema = 'ctgov' 
                    AND table_name = %s
                    ORDER BY ordinal_position;
                """, {"table_name": arguments["table_name"]})
                return [types.TextContent(type="text", text=str(results))]

            elif name == "read-query":
                if not arguments["query"].strip().upper().startswith("SELECT"):
                    raise ValueError("Only SELECT queries are allowed for read-query")
                results = self.db.execute_query(arguments["query"])
                return [types.TextContent(type="text", text=str(results))]

            elif name == "append-insight":
                if "insight" not in arguments:
                    raise ValueError("Missing insight argument")
                self.db.add_insight(arguments["insight"])
                return [types.TextContent(type="text", text="Insight added to memo")]

            elif name == "append-landscape":
                if "finding" not in arguments:
                    raise ValueError("Missing finding argument")
                self.db.add_landscape_finding(arguments["finding"])
                return [types.TextContent(type="text", text="Landscape finding added")]

            elif name == "append-metrics":
                if "metric" not in arguments:
                    raise ValueError("Missing metric argument")
                self.db.add_metrics_finding(arguments["metric"])
                return [types.TextContent(type="text", text="Metric added")]

        except Exception as e:
            if isinstance(e, ValueError):
                raise
            return [types.TextContent(type="text", text=f"Error: {str(e)}")] 