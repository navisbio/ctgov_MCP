"""Database query tools for the AACT database."""

import psycopg2
from ..config import DB_CONFIG
from ..exceptions import QueryError

async def read_query(query: str):
    """Execute a SELECT query on the AACT database."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute(query)
        results = cur.fetchall()
        return results
    except Exception as e:
        raise QueryError(f'Query failed: {str(e)}')
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()
