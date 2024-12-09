from typing import TypedDict
from pydantic import AnyUrl
import mcp.types as types

class ResourceDefinition(TypedDict):
    uri: str
    name: str
    description: str
    mimeType: str

AACT_RESOURCES: list[ResourceDefinition] = [
    {
        "uri": "memo://landscape",
        "name": "Clinical Trial Landscape",
        "description": "Key findings about trial patterns, sponsor activity, and development trends",
        "mimeType": "text/plain",
    },
    {
        "uri": "schema://database",
        "name": "AACT Database Schema",
        "description": "Complete schema information for all tables in the AACT database",
        "mimeType": "application/json",
    }
]

def get_resources() -> list[types.Resource]:
    return [
        types.Resource(
            uri=AnyUrl(resource["uri"]),
            name=resource["name"],
            description=resource["description"],
            mimeType=resource["mimeType"],
        )
        for resource in AACT_RESOURCES
    ] 