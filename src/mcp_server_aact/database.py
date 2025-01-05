import logging
import os
from contextlib import closing
from typing import Any
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
import json
import datetime
from mcp_server_aact.errors import DatabaseError, handle_errors

logger = logging.getLogger('mcp_aact_server.database')

class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.date):
            return obj.isoformat()
        return super().default(obj)

class AACTDatabase:
    def __init__(self):
        logger.info("Initializing AACT database connection")
        load_dotenv()
        
        self.user = os.environ.get("DB_USER")
        self.password = os.environ.get("DB_PASSWORD")
        
        if not self.user or not self.password:
            raise DatabaseError("DB_USER and DB_PASSWORD environment variables must be set")
        
        self.host = "aact-db.ctti-clinicaltrials.org"
        self.database = "aact"
        self._init_database()
        logger.info("AACT database initialization complete")

    @handle_errors(DatabaseError, "Database connection failed: {error}")
    def _init_database(self):
        """Test connection to the AACT database"""
        logger.debug("Testing database connection to AACT")
        with closing(self._get_connection()) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT current_database(), current_schema;")
                db, schema = cur.fetchone()
                logger.info(f"Connected to database: {db}, current schema: {schema}")

    @handle_errors(DatabaseError, "Failed to create database connection: {error}")
    def _get_connection(self):
        """Get a new database connection"""
        logger.debug("Creating new database connection")
        return psycopg2.connect(
            host=self.host,
            database=self.database,
            user=self.user,
            password=self.password
        )

    @handle_errors(DatabaseError, "Database error executing query: {error}")
    def execute_query(self, query: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Execute a SQL query and return results as a list of dictionaries"""
        logger.debug(f"Executing query: {query}")
        if params:
            logger.debug(f"Query parameters: {params}")
        
        with closing(self._get_connection()) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                if params:
                    cur.execute(query, list(params.values()))
                else:
                    cur.execute(query)

                if query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER')):
                    conn.commit()
                    logger.debug(f"Write operation completed. Rows affected: {cur.rowcount}")
                    return [{"affected_rows": cur.rowcount}]

                results = cur.fetchall()
                logger.debug(f"Query returned {len(results)} rows")
                return [dict(row) for row in results]