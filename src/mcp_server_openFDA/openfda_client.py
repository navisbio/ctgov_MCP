import logging
import aiohttp
from typing import Any, Dict, Optional

logger = logging.getLogger('mcp_openfda_server.openfda_client')

class OpenFDAClient:
    """Client for interacting with the OpenFDA API"""
    
    BASE_URL = "https://api.fda.gov"
    
    def __init__(self):
        logger.info("Initializing OpenFDA API client")
        self.session = None
    
    async def _ensure_session(self):
        """Ensure aiohttp session exists"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
    
    async def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a request to the OpenFDA API
        
        Args:
            endpoint: API endpoint (e.g., '/drug/event.json')
            params: Query parameters
            
        Returns:
            JSON response from the API
        """
        await self._ensure_session()
        url = f"{self.BASE_URL}{endpoint}"
        try:
            async with self.session.get(url, params=params) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            logger.error(f"OpenFDA API request failed: {str(e)}", exc_info=True)
            raise RuntimeError(f"OpenFDA API error: {str(e)}")
    
    async def search_drugs(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Search for drugs in OpenFDA
        
        Args:
            query: Search query
            limit: Maximum number of results to return
            
        Returns:
            Search results from OpenFDA
        """
        params = {
            'search': query,
            'limit': limit
        }
        return await self._make_request('/drug/event.json', params)
    
    async def get_drug_events(self, drug_name: str, limit: int = 10) -> Dict[str, Any]:
        """Get adverse events for a specific drug
        
        Args:
            drug_name: Name of the drug
            limit: Maximum number of events to return
            
        Returns:
            Adverse events data from OpenFDA
        """
        params = {
            'search': f'patient.drug.medicinalproduct:"{drug_name}"',
            'limit': limit
        }
        return await self._make_request('/drug/event.json', params)
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session:
            await self.session.close()
            self.session = None

    async def execute_query(
        self, 
        endpoint: str,
        search_query: str = None,
        count: str = None,
        sort: str = None,
        limit: int = 1
    ) -> Dict[str, Any]:
        """Execute a query against OpenFDA API with comprehensive syntax support
        
        Args:
            endpoint: API endpoint (e.g., drug/event)
            search_query: Search query with field:term syntax, supports AND/OR operations
            count: Field to count unique values
            sort: Field and direction for sorting (e.g., receivedate:desc)
            limit: Maximum number of results
            
        Returns:
            Query results from OpenFDA
        """
        params = {}
        
        if search_query:
            params['search'] = search_query
        
        if count:
            params['count'] = count
            
        if sort:
            params['sort'] = sort
            
        if limit and not count:
            params['limit'] = limit

        return await self._make_request(f'/{endpoint}.json', params)
