"""Configuration handling for the AACT MCP server."""

import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST', 'aact-db.ctti-clinicaltrials.org'),
    'database': 'aact'
}
