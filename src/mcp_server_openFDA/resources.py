from typing import TypedDict
from pydantic import AnyUrl
import mcp.types as types

class ResourceDefinition(TypedDict):
    uri: str
    name: str
    description: str
    mimeType: str

OPENFDA_RESOURCES: list[ResourceDefinition] = [
    {
        "uri": "memo://landscape",
        "name": "Drug Insights Landscape",
        "description": "Key findings about drug safety, labeling, and adverse events from OpenFDA data",
        "mimeType": "text/plain",
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
        for resource in OPENFDA_RESOURCES
    ]    