from . import server
import asyncio
import argparse

def main():
    """Main entry point for the OpenFDA MCP Server."""
    parser = argparse.ArgumentParser(description='OpenFDA MCP Server')
    args = parser.parse_args()
    asyncio.run(server.main())

__all__ = ["main", "server"]
