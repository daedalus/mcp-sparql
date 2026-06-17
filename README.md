**mcp-sparql** — MCP server exposing SPARQL query functionalities for LLMs.

[![PyPI](https://img.shields.io/pypi/v/mcp-sparql.svg)](https://pypi.org/project/mcp-sparql/)
[![Python](https://img.shields.io/pypi/pyversions/mcp-sparql.svg)](https://pypi.org/project/mcp-sparql/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/master/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

mcp-name: io.github.daedalus/mcp-sparql

## Install

```bash
pip install mcp-sparql
```

## Usage

### As an MCP Server

Add to your MCP configuration (e.g., `~/.config/claude/mcp.json`):

```json
{
  "mcpServers": {
    "mcp-sparql": {
      "command": "mcp-sparql"
    }
  }
}
```

### Available Tools

| Tool | Description |
|------|-------------|
| `sparql_query` | Execute SPARQL SELECT queries (table or JSON output) |
| `sparql_ask` | Execute SPARQL ASK queries (boolean result) |
| `sparql_construct` | Execute SPARQL CONSTRUCT queries (Turtle or JSON-LD) |
| `sparql_describe` | Execute SPARQL DESCRIBE queries (Turtle or JSON-LD) |
| `sparql_validate` | Validate SPARQL query syntax without executing |
| `sparql_list_graphs` | List named graphs on a SPARQL endpoint |
| `sparql_get_prefixes` | Get common prefixes for a SPARQL endpoint |

### Examples

**Query Wikidata:**

```
sparql_query:
  endpoint: "https://query.wikidata.org/sparql"
  query: "SELECT ?item ?itemLabel WHERE { ?item wdt:P31 wd:Q5 . ?item rdfs:label ?itemLabel . FILTER(LANG(?itemLabel) = 'en') } LIMIT 5"
```

**Check if an entity exists:**

```
sparql_ask:
  endpoint: "https://query.wikidata.org/sparql"
  query: "ASK { wd:Q42 wdt:P31 wd:Q5 }"
```

**Validate a query:**

```
sparql_validate:
  query: "SELECT ?s WHERE { ?s ?p ?o }"
```

**List named graphs:**

```
sparql_list_graphs:
  endpoint: "https://query.wikidata.org/sparql"
```

**Get common prefixes:**

```
sparql_get_prefixes:
  endpoint: "https://query.wikidata.org/sparql"
```

### Resources

| Resource | URI | Description |
|----------|-----|-------------|
| Common Prefixes | `sparql://common-prefixes` | Standard SPARQL namespace prefixes |

## API

### `sparql_query`

Execute a SPARQL SELECT query.

**Parameters:**

- `endpoint` (str): SPARQL endpoint URL
- `query` (str): SPARQL SELECT query
- `timeout` (int, default=30): Query timeout in seconds
- `output_format` (str, default="table"): "table" for Markdown, "json" for JSON
- `headers` (dict, optional): HTTP headers for authentication
- `max_rows` (int, default=1000): Maximum result rows

### `sparql_ask`

Execute a SPARQL ASK query. Returns "true" or "false".

### `sparql_construct`

Execute a SPARQL CONSTRUCT query. Returns RDF triples.

**Additional parameters:**

- `output_format` (str, default="turtle"): "turtle" or "json"

### `sparql_describe`

Execute a SPARQL DESCRIBE query. Returns RDF description.

### `sparql_validate`

Validate SPARQL query syntax without executing.

### `sparql_list_graphs`

List available named graphs on a SPARQL endpoint.

### `sparql_get_prefixes`

Get commonly used prefixes for a SPARQL endpoint.

## Development

```bash
git clone https://github.com/daedalus/mcp-sparql.git
cd mcp-sparql
pip install -e ".[test]"

# run tests
pytest

# format
ruff format src/ tests/

# lint + type check
prospector --with-tool ruff --with-tool mypy --with-tool pylint src/
```
