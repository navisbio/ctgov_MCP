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
        "uri": "memo://insights",
        "name": "Insights on Clinical Trial Landscape",
        "description": "Comprehensive analysis repository capturing key findings about clinical trial patterns, sponsor activities, development trends, and competitive dynamics. This living document grows with each discovered insight to build a complete therapeutic landscape overview.",
        "mimeType": "text/plain",
    },
    {
        "uri": "schema://database",
        "name": "AACT Database Schema",
        "description": "Detailed structural information about the AACT database, including table relationships, column definitions, and data types. Essential reference for understanding data organization and planning effective queries.",
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