# AACT Clinical Trials MCP Server

## Overview
A Model Context Protocol (MCP) server implementation that provides access to the AACT (Aggregate Analysis of ClinicalTrials.gov) database. This server enables analysis of clinical trial data, tracking development trends, and automatically generating analysis memos that capture insights about therapeutic landscapes.

## Components

### Resources
The server exposes a dynamic resources to store analysis results:
- `memo://landscape`: Key findings about trial patterns, sponsor activity, and development trends


### Prompts
The server provides an analytical prompt:
- `indication-landscape`: Interactive prompt that analyzes clinical trial patterns
  - Required argument: `topic` - The therapeutic area or topic to analyze (e.g., "multiple sclerosis", "biomarkers used in breast cancer", ...)
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
   - Add new business insights about trial patterns, development trends, or other parts of the analysis
   - Input:
     - `finding` (string): Analysis finding about trial patterns or trends
   - Returns: Confirmation of insight addition



## Create an Account to Access the Database

AACT requires a free account to access the database. You can sign up at:

https://aact.ctti-clinicaltrials.org/users/sign_up


## Environment Variables
The server requires the following environment variables:
- `DB_USER`: AACT database username
- `DB_PASSWORD`: AACT database password

## Usage with Claude Desktop

Note that you need Claude Desktop and a Claude subscription at the moment. 

Add the following lines to the file claude_desktop_config.json. (On macOS, the file is located at /Users/YOUR_USERNAME/Library/Application Support/Claude/claude_desktop_config.json and you will need to create it yourself if it does not exist yet).

```json
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

Note: Replace `YOUR_AACT_USERNAME` and `YOUR_AACT_PASSWORD` with your actual AACT credentials.


## Roadmap & Contribution

Over the coming weeks and months, we will build other MCP servers for the following datasets:

- OpenFDA: Access to FDA drug, device, and food data
- ChEMBL: Bioactive molecules and drug-like compounds
- Open Targets: Genetic associations and drug target validation
- And more to come!

We warmly welcome contributions of all kinds! Happy to hear from you if you

- Have specific use cases you'd like to explore
- Need customizations for your research
- Want to suggest additional datasets
- Are interested in contributing code, documentation, or ideas
- Want to improve existing features

Please reach out by:
- Opening an issue on GitHub
- Starting a discussion in our repository
- Emailing us at jonas.walheim@navis-bio.com
- Submitting pull requests

Your feedback helps shape our development priorities and align them with the research community's needs.

## License

This MCP server is licensed under the GNU General Public License v3.0 (GPL-3.0). This means you have the freedom to run, study, share, and modify the software. Any modifications or derivative works must also be distributed under the same GPL-3.0 terms. For more details, please see the LICENSE file in the project repository.

## Acknowledgements

This project was inspired by and initially based on code from:
- [SQLite MCP Server](https://github.com/modelcontextprotocol/servers/tree/main/src/sqlite)
- [DuckDB MCP Server](https://github.com/ktanaka101/mcp-server-duckdb/tree/main)
- [OpenDataMCP](https://github.com/OpenDataMCP/OpenDataMCP)

Thanks to these awesome projects for showing us the way! 🙌
