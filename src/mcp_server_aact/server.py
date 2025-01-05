import logging
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
from mcp_server_aact.database import AACTDatabase
from mcp_server_aact.handlers import MCPHandlers
from mcp.types import LoggingLevel, EmptyResult
import json
from pathlib import Path

logger = logging.getLogger('mcp_aact_server')
logger.setLevel(logging.DEBUG)

class AACTServer(Server):
    def __init__(self):
        super().__init__("aact-manager")
        self.db = AACTDatabase()
        
        # Load the schema resource
        schema_path = Path(__file__).parent / "resources" / "database_schema.json"
        with open(schema_path) as f:
            self.schema = json.load(f)
        
        # Pass schema to handlers
        self.handlers = MCPHandlers(self.db, self.schema)
        self._register_handlers()
        
        # Set up logging handler that sends to MCP client
        self.log_handler = MCPLogHandler(self)
        logger.addHandler(self.log_handler)

    def _register_handlers(self):
        @self.list_resources()
        async def handle_list_resources():
            return await self.handlers.handle_list_resources()

        @self.read_resource()
        async def handle_read_resource(uri):
            return await self.handlers.handle_read_resource(uri)

        @self.list_prompts()
        async def handle_list_prompts():
            return await self.handlers.handle_list_prompts()

        @self.get_prompt()
        async def handle_get_prompt(name, arguments):
            return await self.handlers.handle_get_prompt(name, arguments)

        @self.list_tools()
        async def handle_list_tools():
            return await self.handlers.handle_list_tools()

        @self.call_tool()
        async def handle_call_tool(name, arguments):
            return await self.handlers.handle_call_tool(name, arguments)

        @self.set_logging_level()
        async def handle_set_logging_level(level: LoggingLevel) -> EmptyResult:
            """Handle requests to change the logging level"""
            logger.info(f"Setting logging level to {level}")
            logging.getLogger('mcp_aact_server').setLevel(level.upper())
            return EmptyResult()

class MCPLogHandler(logging.Handler):
    def __init__(self, server):
        super().__init__()
        self.server = server

    def emit(self, record):
        try:
            msg = self.format(record)
            # Just log to standard logger instead of trying to send to session
            logger.log(record.levelno, msg)
        except Exception:
            self.handleError(record)

async def main():
    try:
        server = AACTServer()
        
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="aact",
                    server_version="0.1.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )
    except Exception as e:
        logger.error(f"Server error: {str(e)}", exc_info=True)
        raise