"""Custom exceptions for the AACT MCP server."""

class CTGovError(Exception):
    """Base exception for CTGOV errors"""
    pass

class QueryError(CTGovError):
    """Query execution failed"""
    pass

class ResourceError(CTGovError):
    """Resource access or creation failed"""
    pass
