import logging
from mcp.server import Server, NotificationOptions, RequestContext
from mcp.server.models import InitializationOptions
import mcp.server.stdio
from .database import AACTDatabase
from .handlers import MCPHandlers

logger = logging.getLogger('mcp_aact_server')
logger.setLevel(logging.DEBUG)

class AACTServer(Server):
    def __init__(self):
        super().__init__("aact-manager")
        self.db = AACTDatabase()
        self.handlers = MCPHandlers(self.db)
        self._register_handlers()

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
        logger.error(f"Server error: {str(e)}")
        raise
