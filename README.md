# AACT Clinical Trials MCP Server

## Overview
A Model Context Protocol (MCP) server implementation that provides access to the AACT (Aggregate Analysis of ClinicalTrials.gov) database. This server enables analysis of clinical trial data, tracking development trends, and automatically generating analysis memos that capture insights about therapeutic landscapes.

## Components

### Resources
The server exposes three dynamic resources:
- `memo://landscape`: Key findings about trial patterns, sponsor activity, and development trends
- `memo://metrics`: Quantitative metrics about trial phases, success rates, and temporal trends

### Prompts
The server provides an analytical prompt:
- `indication-landscape`: Interactive prompt that analyzes clinical trial patterns
  - Required argument: `topic` - The therapeutic area to analyze (e.g., "multiple sclerosis", "breast cancer")
  - Analyzes trial patterns and development trends
  - Examines competitive dynamics
  - Integrates findings with the landscape and metrics memos

### Tools
The server offers several core tools:

#### Query Tools
- `read-query`
   - Execute SELECT queries on the AACT database
   - Input: 
     - `query` (string): The SELECT SQL query to execute
   - Returns: Query results as array of objects

#### Schema Tools
- `list-tables`
   - Get a list of all tables in the AACT database
   - No input required
   - Returns: Array of table names

- `describe-table`
   - View schema information for a specific table
   - Input:
     - `table_name` (string): Name of table to describe
   - Returns: Array of column definitions with names and types

#### Analysis Tools
- `append-insight`
   - Add new business insights to the insights memo
   - Input:
     - `insight` (string): Business insight discovered from data analysis
   - Returns: Confirmation of insight addition

- `append-landscape`
   - Add findings about trial patterns and development trends
   - Input:
     - `finding` (string): Analysis finding about trial patterns or trends
   - Returns: Confirmation of finding addition

- `append-metrics`
   - Add quantitative metrics about trials
   - Input:
     - `metric` (string): Quantitative metric or statistical finding
   - Returns: Confirmation of metric addition

## Create an Account to Access the Database

AACT requires a free account to access the database. You can sign up at:

https://aact.ctti-clinicaltrials.org/users/sign_up

## Usage with Claude Desktop

Add the server to your claude_desktop_config.json

On macOS, the file is located at:
/Users/YOUR_USERNAME/Library/Application Support/Claude/claude_desktop_config.json

```bash
"mcpServers": {
    "CTGOV-MCP": {
      "command": "uvx",
      "args": [
        "mcp-server-aact"
      ],
      "env": {
        "DB_USER": USERNAME,
        "DB_PASSWORD": PASSWORD
      }
    }
}
```

## Environment Variables
The server requires the following environment variables:
- `DB_USER`: AACT database username
- `DB_PASSWORD`: AACT database password

## License

This MCP server is licensed under the GNU General Public License v3.0 (GPL-3.0). This means you have the freedom to run, study, share, and modify the software. Any modifications or derivative works must also be distributed under the same GPL-3.0 terms. For more details, please see the LICENSE file in the project repository.

## Acknowledgements

This project was inspired by and initially based on code from:
- [SQLite MCP Server](https://github.com/modelcontextprotocol/servers/tree/main/src/sqlite)
- [DuckDB MCP Server](https://github.com/ktanaka101/mcp-server-duckdb/tree/main)
- [OpenDataMCP](https://github.com/OpenDataMCP/OpenDataMCP)

Thanks to these awesome projects for showing us the way! 🙌
