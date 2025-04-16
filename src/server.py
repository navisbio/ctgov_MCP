import logging
import json
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from .database import AACTDatabase
from .memo_manager import MemoManager

# Load environment variables
load_dotenv()

# Setup logging
logger = logging.getLogger('mcp_aact_server')
logger.setLevel(logging.DEBUG)

# Create database and memo manager instances
db = AACTDatabase()
memo_manager = MemoManager()

# Create an MCP server
mcp = FastMCP("AACT Clinical Trials Database")

# Load the schema resource
schema_path = Path(__file__).parent / "resources" / "database_schema.json"
try:
    with open(schema_path) as f:
        schema = json.load(f)
except Exception as e:
    logger.error(f"Error loading schema: {e}")
    schema = {}

@mcp.resource("schema://database")
def get_schema() -> str:
    """Return the database schema as a resource"""
    return json.dumps(schema, indent=2)

@mcp.resource("memo://insights")
def get_insights_memo() -> str:
    """Return the memo of insights as a resource"""
    return memo_manager.get_insights_memo()

@mcp.tool()
def list_tables() -> str:
    """Get an overview of all available tables in the AACT database. 
    This tool helps you understand the database structure before starting your analysis 
    to identify relevant data sources."""
    try:
        results = db.execute_query("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'ctgov'
            ORDER BY table_name;
        """)
        logger.info(f"Retrieved {len(results)} tables")
        return str(results)
    except Exception as e:
        logger.error(f"Error listing tables: {e}")
        return f"Error: {str(e)}"

@mcp.tool()
def describe_table(table_name: str) -> str:
    """Examine the detailed structure of a specific AACT table, including column names and data types.
    Use this before querying to ensure you target the right columns and understand the data format."""
    if not table_name:
        raise Exception("Missing table_name argument")
    
    try:
        results = db.execute_query("""
            SELECT column_name, data_type, character_maximum_length
            FROM information_schema.columns
            WHERE table_schema = 'ctgov' 
            AND table_name = %s
            ORDER BY ordinal_position;
        """, {"table_name": table_name})
        
        logger.info(f"Retrieved {len(results)} columns for table {table_name}")
        return str(results)
    except Exception as e:
        logger.error(f"Error describing table: {e}")
        return f"Error: {str(e)}"

@mcp.tool()
def read_query(query: str) -> str:
    """Execute a SELECT query on the AACT clinical trials database. 
    Use this tool to extract and analyze specific data from any table."""
    if not query:
        raise Exception("Missing query argument")
    
    # Simple validation to prevent destructive queries
    query = query.strip()
    if not query.upper().startswith("SELECT"):
        return "Error: Only SELECT queries are allowed"
    
    try:
        results = db.execute_query(query)
        logger.info(f"Query returned {len(results)} rows")
        return str(results)
    except Exception as e:
        logger.error(f"Error executing query: {e}")
        return f"Error: {str(e)}"

@mcp.tool()
def append_insight(finding: str) -> str:
    """Record key findings and insights discovered during your analysis. 
    Use this tool whenever you uncover meaningful patterns, trends, or notable observations 
    about clinical trials. This helps build a comprehensive analytical narrative 
    and ensures important discoveries are documented."""
    if not finding:
        raise Exception("Missing finding argument")
    
    try:
        memo_manager.add_insights(finding)
        logger.info("Insight added successfully")
        return "Insight added successfully"
    except Exception as e:
        logger.error(f"Error adding insight: {e}")
        return f"Error: {str(e)}"

def main():
    """Main entry point for the server"""
    try:
        # Will shut down gracefully
        mcp.run()
    except Exception as e:
        logger.error(f"Server error: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()