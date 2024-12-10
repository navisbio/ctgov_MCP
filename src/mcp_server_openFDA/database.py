import logging
from typing import Any, Dict, List
import json
import datetime
from .openfda_client import OpenFDAClient

logger = logging.getLogger('mcp_openfda_server.database')

class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.date):
            return obj.isoformat()
        return super().default(obj)

class OpenFDADatabase:
    def __init__(self):
        logger.info("Initializing OpenFDA client")
        self.client = OpenFDAClient()
        logger.info("OpenFDA client initialization complete")

    async def execute_query(self, query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Execute a query against OpenFDA API
        
        This method maintains compatibility with the old interface while using the new OpenFDA client
        
        Args:
            query: Search query for OpenFDA
            params: Additional parameters for the API
            
        Returns:
            List of results from OpenFDA
        """
        try:
            # Convert the query to OpenFDA format
            # For now, we'll just pass it through to the search_drugs method
            result = await self.client.search_drugs(query)
            
            # Convert the response to match the expected format
            # This will need to be adjusted based on the specific needs of your application
            return result.get('results', [])
        except Exception as e:
            logger.error(f"OpenFDA API error: {str(e)}", exc_info=True)
            raise RuntimeError(f"OpenFDA API error: {str(e)}")

    async def get_drug_events(self, drug_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get adverse events for a specific drug
        
        Args:
            drug_name: Name of the drug
            limit: Maximum number of events to return
            
        Returns:
            List of adverse events
        """
        try:
            result = await self.client.get_drug_events(drug_name, limit)
            return result.get('results', [])
        except Exception as e:
            logger.error(f"OpenFDA API error: {str(e)}", exc_info=True)
            raise RuntimeError(f"OpenFDA API error: {str(e)}")
            
    async def close(self):
        """Close the OpenFDA client session"""
        await self.client.close()