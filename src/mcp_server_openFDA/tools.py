import logging
from typing import Any
import mcp.types as types
from .openfda_client import OpenFDAClient
from .memo_manager import MemoManager
import json

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
                description="Execute queries against the OpenFDA API with comprehensive syntax support",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "endpoint": {
                            "type": "string",
                            "description": "API endpoint (e.g., drug/event)",
                            "default": "drug/event"
                        },
                        "search_query": {
                            "type": "string",
                            "description": "OpenFDA search query using field:term syntax. Supports AND/OR operations"
                        },
                        "count": {
                            "type": "string",
                            "description": "Field to count unique values"
                        },
                        "sort": {
                            "type": "string",
                            "description": "Field and direction for sorting (e.g., receivedate:desc)"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results",
                            "default": 1
                        }
                    }
                }
            ),            types.Tool(
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
                    "drug/label", "drug/event", "drug/ndc", "drug/enforcement"
                ]
                return [types.TextContent(type="text", text=str(endpoints))]

            elif name == "describe-table":
                endpoint_fields = {
                    "drug/label": [
                        "effective_time",
                        "abuse",
                        "active_ingredient",
                        "adverse_reactions",
                        "boxed_warning",
                        "clinical_pharmacology",
                        "clinical_studies",
                        "contraindications", 
                        "description",
                        "dosage_and_administration",
                        "drug_interactions",
                        "indications_and_usage",
                        "warnings",
                        "pregnancy",
                        "nursing_mothers",
                        "pediatric_use",
                        "geriatric_use",
                        "mechanism_of_action",
                        "pharmacodynamics",
                        "pharmacokinetics",
                        "nonclinical_toxicology",
                        "microbiology"
                    ],
                    "drug/event": [
                        "safetyreportid",
                        "patient.drug.medicinalproduct",
                        "patient.drug.drugcharacterization",
                        "patient.reaction.reactionmeddrapt",
                        "occurcountry",
                        "receiptdate",
                        "serious",
                        "seriousnessdeath",
                        "seriousnesshospitalization"
                    ],
                    "drug/ndc": [
                        "product_ndc",
                        "generic_name",
                        "brand_name",
                        "dosage_form",
                        "route",
                        "marketing_status",
                        "active_ingredients"
                    ],
                    "drug/enforcement": [
                        "recall_number",
                        "reason_for_recall",
                        "status",
                        "distribution_pattern",
                        "product_quantity",
                        "recall_initiation_date",
                        "state",
                        "event_id",
                        "product_type",
                        "product_description",
                        "country",
                        "city",
                        "recalling_firm",
                        "voluntary_mandated"
                    ]
                }
                
                table_name = arguments.get("table_name")
                if table_name not in endpoint_fields:
                    raise ValueError(f"Unknown endpoint: {table_name}. Available endpoints: {', '.join(endpoint_fields.keys())}")
                    
                fields_info = {
                    "endpoint": table_name,
                    "available_fields": endpoint_fields[table_name],
                    "query_example": f"https://api.fda.gov/{table_name}.json?search=field:value&limit=1"
                }
                
                return [types.TextContent(type="text", text=json.dumps(fields_info, indent=2))]

            elif name == "read-query":
                endpoint = arguments.get("endpoint", "drug/label")
                search_query = arguments.get("query", "").strip()
                limit = arguments.get("limit", 1)
                count = arguments.get("count")
                sort = arguments.get("sort")
                
                result = await self.client.execute_query(
                    endpoint=endpoint,
                    search_query=search_query,
                    count=count,
                    sort=sort,
                    limit=limit
                )
                
                return [types.TextContent(
                    type="text", 
                    text=json.dumps(result, indent=2)
                )]

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