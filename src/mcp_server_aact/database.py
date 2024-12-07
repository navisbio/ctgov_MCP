import logging
import os
from contextlib import closing
from typing import Any, List
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
import json
import datetime

logger = logging.getLogger('mcp_aact_server.database')

class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.date):
            return obj.isoformat()
        return super().default(obj)

class AACTDatabase:
    def __init__(self, server=None):
        self.server = server
        # Load environment variables
        load_dotenv()
        
        # Get AACT credentials from environment
        self.user = os.environ.get("DB_USER")
        self.password = os.environ.get("DB_PASSWORD")
        
        if not self.user or not self.password:
            raise ValueError("DB_USER and DB_PASSWORD environment variables must be set")
        
        self.host = "aact-db.ctti-clinicaltrials.org"
        self.database = "aact"
        self.insights: list[str] = []
        self.landscape_findings: list[str] = []  # Store landscape findings in memory
        self.metrics_findings: list[str] = []    # Store metrics in memory
        self._init_database()

    def _log(self, level: str, message: str):
        """Helper method to log messages through MCP if available"""
        if hasattr(self, 'server') and self.server and hasattr(self.server, 'request_context'):
            self.server.request_context.session.send_log_message(level=level, data=message)
        else:
            logger.log(getattr(logging, level.upper()), message)

    def _init_database(self):
        """Test connection to the AACT database"""
        self._log("debug", "Testing database connection to AACT")
        try:
            with closing(self._get_connection()) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT current_database(), current_schema;")
                    db, schema = cur.fetchone()
                    self._log("info", f"Connected to database: {db}, current schema: {schema}")
                conn.close()
        except Exception as e:
            self._log("error", f"Database connection failed: {str(e)}")
            raise

    def _get_connection(self):
        """Get a new database connection"""
        return psycopg2.connect(
            host=self.host,
            database=self.database,
            user=self.user,
            password=self.password
        )

    def execute_query(self, query: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Execute a SQL query and return results as a list of dictionaries"""
        self._log("debug", f"Executing query: {query}")
        if params:
            self._log("debug", f"Query parameters: {params}")
        
        try:
            with closing(self._get_connection()) as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                    if params:
                        cur.execute(query, list(params.values()))
                    else:
                        cur.execute(query)

                    if query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER')):
                        conn.commit()
                        self._log("debug", f"Write operation completed. Rows affected: {cur.rowcount}")
                        return [{"affected_rows": cur.rowcount}]

                    results = cur.fetchall()
                    self._log("debug", f"Query returned {len(results)} rows")
                    return [dict(row) for row in results]

        except Exception as e:
            self._log("error", f"Database error executing query: {str(e)}")
            raise

    def add_insight(self, insight: str):
        """Add a business insight to the collection"""
        self.insights.append(insight)
        logger.debug(f"Added new insight. Total insights: {len(self.insights)}")

    def get_insights_memo(self) -> str:
        """Generate a formatted memo from collected insights"""
        logger.debug(f"Generating memo with {len(self.insights)} insights")
        if not self.insights:
            return "No business insights have been discovered yet."

        insights = "\n".join(f"- {insight}" for insight in self.insights)

        memo = "📊 Clinical Trials Intelligence Memo\n\n"
        memo += "Key Insights Discovered:\n\n"
        memo += insights

        if len(self.insights) > 1:
            memo += "\nSummary:\n"
            memo += f"Analysis has revealed {len(self.insights)} key insights about clinical trials and drug development."

        return memo 

    def get_landscape_memo(self) -> str:
        """Generate a formatted memo from collected landscape findings"""
        logger.debug(f"Generating landscape memo with {len(self.landscape_findings)} findings")
        if not self.landscape_findings:
            return "No landscape analysis available yet."

        findings = "\n".join(f"- {finding}" for finding in self.landscape_findings)

        memo = "🔍 Clinical Trial Landscape Analysis\n\n"
        memo += "Key Development Patterns & Trends:\n\n"
        memo += findings

        if len(self.landscape_findings) > 1:
            memo += "\n\nSummary:\n"
            memo += f"Analysis has identified {len(self.landscape_findings)} key patterns in trial development."

        return memo

    def get_metrics_memo(self) -> str:
        """Generate a formatted memo from collected metrics"""
        logger.debug(f"Generating metrics memo with {len(self.metrics_findings)} metrics")
        if not self.metrics_findings:
            return "No metrics available yet."

        metrics = "\n".join(f"- {metric}" for metric in self.metrics_findings)

        memo = "📊 Clinical Trial Metrics Summary\n\n"
        memo += "Key Quantitative Findings:\n\n"
        memo += metrics

        if len(self.metrics_findings) > 1:
            memo += "\n\nOverview:\n"
            memo += f"Analysis has captured {len(self.metrics_findings)} key metrics about trial activity."

        return memo

    def add_landscape_finding(self, finding: str) -> None:
        """Add a new landscape finding to the in-memory collection"""
        self.landscape_findings.append(finding)
        logger.debug(f"Added new landscape finding. Total findings: {len(self.landscape_findings)}")

    def add_metrics_finding(self, metric: str) -> None:
        """Add a new metric to the in-memory collection"""
        self.metrics_findings.append(metric)
        logger.debug(f"Added new metric. Total metrics: {len(self.metrics_findings)}")