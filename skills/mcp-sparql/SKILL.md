## name: mcp-sparql description: > MCP server exposing SPARQL query functionalities for LLMs. Triggers on keywords: SPARQL, RDF, triple store, knowledge graph, Wikidata, DBpedia, SPARQL endpoint, query RDF data.

# mcp-sparql Skill

Exposes SPARQL query capabilities to LLMs via the Model Context Protocol.
Supports SELECT, ASK, CONSTRUCT, and DESCRIBE queries against any SPARQL endpoint.

## Usage

Add to your MCP configuration:

```json
{
  "mcpServers": {
    "mcp-sparql": {
      "command": "mcp-sparql"
    }
  }
}
```

## Available Tools

- `sparql_query` — Execute SELECT queries, return table or JSON
- `sparql_ask` — Execute ASK queries, return boolean
- `sparql_construct` — Execute CONSTRUCT queries, return RDF triples
- `sparql_describe` — Execute DESCRIBE queries, return RDF description
- `sparql_validate` — Validate SPARQL syntax without executing
- `sparql_list_graphs` — List named graphs on an endpoint
- `sparql_get_prefixes` — Get common prefixes for an endpoint

## Examples

Query Wikidata for the capital of France:

```json
{
  "endpoint": "https://query.wikidata.org/sparql",
  "query": "SELECT ?capitalLabel WHERE { wd:Q142 wdt:P36 ?capital . ?capital rdfs:label ?capitalLabel . FILTER(LANG(?capitalLabel) = 'en') }"
}
```
