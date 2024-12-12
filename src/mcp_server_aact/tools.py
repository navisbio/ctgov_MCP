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
                description="Execute a SELECT query on the AACT clinical trials database. Use this tool to extract and analyze specific data from any table.",
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
                description="Get an overview of all available tables in the AACT database. This tool helps you understand the database structure before starting your analysis to identify relevant data sources.",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
            types.Tool(
                name="describe-table",
                description="Examine the detailed structure of a specific AACT table, including column names and data types. Use this before querying to ensure you target the right columns and understand the data format.",
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
                description="Record key findings and insights discovered during your analysis. Use this tool whenever you uncover meaningful patterns, trends, or notable observations about clinical trials. This helps build a comprehensive analytical narrative and ensures important discoveries are documented.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "finding": {"type": "string", "description": "Analysis finding about trial patterns or trends"},
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

            elif name == "append-insight":
                if "finding" not in arguments:
                    logger.error("Missing finding argument for append-insight")
                    raise ValueError("Missing finding argument")
                
                logger.debug(f"Adding insight: {arguments['finding'][:50]}...")
                self.memo_manager.add_insights(arguments["finding"])
                logger.info("Landscape finding added successfully")
                return [types.TextContent(type="text", text="Insight added")]


        except Exception as e:
            logger.error(f"Error executing tool {name}: {str(e)}", exc_info=True)
            raise
 