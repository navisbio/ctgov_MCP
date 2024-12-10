import logging
from typing import Any
import mcp.types as types
from .openfda_client import OpenFDAClient
from .memo_manager import MemoManager

logger = logging.getLogger('mcp_openfda_server.tools')

class ToolManager:
    def __init__(self, openfda_client: OpenFDAClient, memo_manager: MemoManager):
        self.client = openfda_client
        self.memo_manager = memo_manager
        logger.info("ToolManager initialized")

    def get_available_tools(self) -> list[types.Tool]:
        """Return list of available tools"""
        logger.debug("Retrieving available tools")
        tools = [
            types.Tool(
                name="read-query",
                description="Execute a query on the OpenFDA API for drug information",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "OpenFDA API search query"},
                        "endpoint": {"type": "string", "description": "API endpoint (e.g., drugsfda, label, ndc)", "default": "drugsfda"}
                    },
                    "required": ["query"],
                },
            ),
            types.Tool(
                name="list-tables",
                description="List all available OpenFDA drug endpoints",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
            types.Tool(
                name="describe-table",
                description="Get the available fields for a specific OpenFDA endpoint",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {"type": "string", "description": "Name of the endpoint to describe (e.g., drugsfda, label, ndc)"},
                    },
                    "required": ["table_name"],
                },
            ),
            types.Tool(
                name="append-landscape",
                description="Add findings and insights related to the drug analysis to the memo",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "finding": {"type": "string", "description": "Analysis finding about drug patterns or trends"},
                    },
                    "required": ["finding"],
                },
            ),
        ]
        logger.debug(f"Retrieved {len(tools)} available tools")
        return tools

    async def execute_tool(self, name: str, arguments: dict[str, Any] | None) -> list[types.TextContent]:
        """Execute a tool with given arguments"""
        logger.info(f"Executing tool: {name} with arguments: {arguments}")
        
        try:
            if name not in {tool.name for tool in self.get_available_tools()}:
                logger.error(f"Unknown tool requested: {name}")
                raise ValueError(f"Unknown tool: {name}")

            if not arguments and name != "list-tables":
                logger.error("Missing required arguments for tool execution")
                raise ValueError("Missing required arguments")

            if name == "list-tables":
                endpoints = [
                    "drugsfda", "label", "ndc", "enforcement", 
                    "event", "recall"
                ]
                return [types.TextContent(type="text", text=str(endpoints))]

            elif name == "describe-table":
                endpoint_fields = {
                    "drugsfda": ["application_number", "sponsor_name", "products"],
                    "label": ["id", "effective_time", "drug_interactions"],
                    "ndc": ["product_ndc", "generic_name", "brand_name"],
                }
                table_name = arguments.get("table_name")
                if table_name not in endpoint_fields:
                    raise ValueError(f"Unknown endpoint: {table_name}")
                return [types.TextContent(type="text", text=str(endpoint_fields[table_name]))]

            elif name == "read-query":
                endpoint = arguments.get("endpoint", "drugsfda")
                query = arguments.get("query", "").strip()
                
                # Use the OpenFDA client from our database object
                result = await self.db.execute_query(query, {"endpoint": endpoint})
                return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

            elif name == "append-landscape":
                if "finding" not in arguments:
                    logger.error("Missing finding argument for append-landscape")
                    raise ValueError("Missing finding argument")
                
                logger.debug(f"Adding landscape finding: {arguments['finding'][:50]}...")
                self.memo_manager.add_landscape_finding(arguments["finding"])
                logger.info("Landscape finding added successfully")
                return [types.TextContent(type="text", text="Landscape finding added")]

        except Exception as e:
            logger.error(f"Error executing tool {name}: {str(e)}", exc_info=True)
            raise