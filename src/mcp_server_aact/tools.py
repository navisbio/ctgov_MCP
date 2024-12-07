import logging
from typing import Any
import mcp.types as types
from .database import AACTDatabase
from .memo_manager import MemoManager

logger = logging.getLogger('mcp_aact_server.tools')

class ToolManager:
    def __init__(self, db: AACTDatabase, memo_manager: MemoManager):
        self.db = db
        self.memo_manager = memo_manager
        logger.info("ToolManager initialized")

    def get_available_tools(self) -> list[types.Tool]:
        """Return list of available tools"""
        logger.debug("Retrieving available tools")
        tools = [
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
                logger.debug("Executing list-tables query")
                results = self.db.execute_query("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'ctgov'
                    ORDER BY table_name;
                """)
                logger.info(f"Retrieved {len(results)} tables")
                return [types.TextContent(type="text", text=str(results))]

            elif name == "describe-table":
                if "table_name" not in arguments:
                    logger.error("Missing table_name argument for describe-table")
                    raise ValueError("Missing table_name argument")
                
                logger.debug(f"Describing table: {arguments['table_name']}")
                results = self.db.execute_query("""
                    SELECT column_name, data_type, character_maximum_length
                    FROM information_schema.columns
                    WHERE table_schema = 'ctgov' 
                    AND table_name = %s
                    ORDER BY ordinal_position;
                """, {"table_name": arguments["table_name"]})
                logger.info(f"Retrieved {len(results)} columns for table {arguments['table_name']}")
                return [types.TextContent(type="text", text=str(results))]

            elif name == "read-query":
                query = arguments.get("query", "").strip()
                if not query.upper().startswith("SELECT"):
                    logger.error(f"Invalid query type attempted: {query[:50]}...")
                    raise ValueError("Only SELECT queries are allowed for read-query")
                
                logger.debug(f"Executing query: {query}")
                results = self.db.execute_query(query)
                logger.info(f"Query returned {len(results)} rows")
                return [types.TextContent(type="text", text=str(results))]

            elif name == "append-landscape":
                if "finding" not in arguments:
                    logger.error("Missing finding argument for append-landscape")
                    raise ValueError("Missing finding argument")
                
                logger.debug(f"Adding landscape finding: {arguments['finding'][:50]}...")
                self.memo_manager.add_landscape_finding(arguments["finding"])
                logger.info("Landscape finding added successfully")
                return [types.TextContent(type="text", text="Landscape finding added")]

            elif name == "append-metrics":
                if "metric" not in arguments:
                    logger.error("Missing metric argument for append-metrics")
                    raise ValueError("Missing metric argument")
                
                logger.debug(f"Adding metric: {arguments['metric'][:50]}...")
                self.memo_manager.add_metrics_finding(arguments["metric"])
                logger.info("Metric added successfully")
                return [types.TextContent(type="text", text="Metric added")]

        except Exception as e:
            logger.error(f"Error executing tool {name}: {str(e)}", exc_info=True)
            raise
 