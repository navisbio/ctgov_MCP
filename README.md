# AACT Clinical Trials MCP Server

## Overview
A Model Context Protocol (MCP) server implementation that provides access to the AACT (Aggregate Analysis of ClinicalTrials.gov) database. This server enables analysis of clinical trial data, tracking development trends, and automatically generating analysis memos that capture insights about therapeutic landscapes.

## Components

### Resources
- `memo://insights`: Stores analysis findings and insights about clinical trial patterns
- `schema://database`: Database schema information

### Prompts
- `indication-landscape`: Analyzes clinical trial patterns for a given therapeutic area
  - Required: `topic` (e.g., "multiple sclerosis", "breast cancer")

### Tools
- `read-query`: Execute SELECT queries on the AACT database
- `list-tables`: Get available tables in the AACT database
- `describe-table`: View schema information for a specific table
- `append-insight`: Add new analysis findings

## Setup

### Database Access
1. Create a free account at https://aact.ctti-clinicaltrials.org/users/sign_up
2. Set environment variables:
   - `DB_USER`: AACT database username
   - `DB_PASSWORD`: AACT database password

## Usage with Claude Desktop

Note that you need Claude Desktop and a Claude subscription at the moment. 

Add one of the following configurations to the file claude_desktop_config.json. (On macOS, the file is located at /Users/YOUR_USERNAME/Library/Application Support/Claude/claude_desktop_config.json and you will need to create it yourself if it does not exist yet).

### Option 1: Using the published package
```json
"mcpServers": {
    "CTGOV-MCP": {
      "command": "uvx",
      "args": [
        "mcp-server-aact"
      ],
      "env": {
        "DB_USER": "USERNAME",
        "DB_PASSWORD": "PASSWORD"
      }
    }
}
```

### Option 2: Running from source (development)
```json
"mcpServers": {
    "CTGOV-MCP-DEV": {
      "command": "uv",
      "args": [
        "--directory",
        "PATH_TO_REPOSITORY",
        "run",
        "mcp-server-aact"
      ],
      "env": {
        "DB_USER": "USERNAME",
        "DB_PASSWORD": "PASSWORD"
      }
    }
}
```

## Contributing
We welcome contributions! Please:
- Open an issue on GitHub
- Start a discussion
- Email: jonas.walheim@navis-bio.com

## License
GNU General Public License v3.0 (GPL-3.0)

## Acknowledgements

This project was inspired by and initially based on code from:
- [SQLite MCP Server](https://github.com/modelcontextprotocol/servers/tree/main/src/sqlite)
- [DuckDB MCP Server](https://github.com/ktanaka101/mcp-server-duckdb/tree/main)
- [OpenDataMCP](https://github.com/OpenDataMCP/OpenDataMCP)

Thanks to these awesome projects for showing us the way! 🙌

