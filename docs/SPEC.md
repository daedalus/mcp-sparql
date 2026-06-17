# SPEC.md — mcp-sparql

## Purpose

An MCP server that exposes SPARQL query functionalities, enabling LLMs to query RDF triple stores (e.g., Wikidata, DBpedia, custom SPARQL endpoints) via the Model Context Protocol. Supports executing SPARQL queries (SELECT, ASK, CONSTRUCT, DESCRIBE), listing available named graphs, fetching prefix definitions, and validating query syntax.

## Scope

### In Scope

- Execute SPARQL SELECT queries against configurable endpoints
- Execute SPARQL ASK queries (boolean results)
- Execute SPARQL CONSTRUCT queries (return RDF triples)
- Execute SPARQL DESCRIBE queries (return RDF descriptions)
- Query syntax validation (parse-only mode)
- List named graphs on a SPARQL endpoint
- Fetch commonly used prefixes for a SPARQL endpoint
- Support for both synchronous and timeout-limited queries
- Configurable SPARQL endpoint URL (per-tool or global)
- Support for query parameters and custom HTTP headers (e.g., Authorization)
- Return results in both table (Markdown) and JSON formats

### Not in Scope

- RDF serialization/deserialization beyond SPARQL result sets
- Graph mutation (INSERT/DELETE/UPDATE) — read-only for safety
- SPARQL endpoint administration
- RDF file format conversion
- Federated SPARQL query composition
- Persistent query caching

## Public API / Interface

### Tools

| Tool | Description |
|------|-------------|
| `sparql_query` | Execute a SPARQL SELECT query and return results as a Markdown table or JSON |
| `sparql_ask` | Execute a SPARQL ASK query and return a boolean result |
| `sparql_construct` | Execute a SPARQL CONSTRUCT query and return RDF triples |
| `sparql_describe` | Execute a SPARQL DESCRIBE query and return an RDF resource description |
| `sparql_validate` | Validate SPARQL query syntax without executing it |
| `sparql_list_graphs` | List available named graphs on a SPARQL endpoint |
| `sparql_get_prefixes` | Get commonly used prefixes for a SPARQL endpoint |

### Tool Signatures

```python
sparql_query(
    endpoint: str,
    query: str,
    timeout: int = 30,
    output_format: Literal["table", "json"] = "table",
    headers: dict[str, str] | None = None,
) -> str
```

```python
sparql_ask(
    endpoint: str,
    query: str,
    timeout: int = 30,
    headers: dict[str, str] | None = None,
) -> str
```

```python
sparql_construct(
    endpoint: str,
    query: str,
    timeout: int = 30,
    output_format: Literal["turtle", "json"] = "turtle",
    headers: dict[str, str] | None = None,
) -> str
```

```python
sparql_describe(
    endpoint: str,
    query: str,
    timeout: int = 30,
    output_format: Literal["turtle", "json"] = "turtle",
    headers: dict[str, str] | None = None,
) -> str
```

```python
sparql_validate(
    query: str,
) -> str
```

```python
sparql_list_graphs(
    endpoint: str,
    timeout: int = 30,
    headers: dict[str, str] | None = None,
) -> str
```

```python
sparql_get_prefixes(
    endpoint: str,
    timeout: int = 30,
    headers: dict[str, str] | None = None,
) -> str
```

### Resources

| Resource | URI | Description |
|----------|-----|-------------|
| `sparql://common-prefixes` | `sparql://common-prefixes` | Common SPARQL namespace prefixes (rdf, rdfs, owl, xsd, etc.) |

## Data Formats

### SPARQL SELECT Results (table format)

Returned as a Markdown table with headers from the query variables.

### SPARQL SELECT Results (json format)

Returned as a JSON array of objects, one per solution mapping.

### SPARQL ASK Results

A string: `"true"` or `"false"`.

### SPARQL CONSTRUCT/DESCRIBE Results

Returned as Turtle RDF or JSON-LD depending on `output_format`.

## Edge Cases

1. Empty result sets — return `"No results found."` instead of an empty table
1. Query timeout — return a clear timeout error message with the timeout value
1. Malformed SPARQL — return validation error with parser error details
1. Endpoint unreachable — return connection error with endpoint URL
1. Very large result sets — limit results to 1000 rows with a warning
1. Invalid HTTP headers — reject and report clearly
1. Empty or null endpoint URL — reject with clear error message

## Performance & Constraints

- Default query timeout: 30 seconds
- Maximum result rows: 1000 (configurable per query)
- HTTP client: `httpx` for async support
- SPARQL parsing: `rdflib` for query validation
- No caching layer — queries always hit the endpoint
