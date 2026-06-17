"""MCP server exposing SPARQL query functionalities."""

from __future__ import annotations

import json
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP
from rdflib import Graph

from mcp_sparql.core.models import (
    OutputFormat,
    RDFOutputFormat,
    SparqlAskInput,
    SparqlConstructInput,
    SparqlDescribeInput,
    SparqlGetPrefixesInput,
    SparqlListGraphsInput,
    SparqlQueryInput,
    SparqlValidateInput,
)
from mcp_sparql.core.sparql_client import (
    execute_sparql_ask,
    execute_sparql_construct,
    execute_sparql_describe,
    execute_sparql_select,
    get_endpoint_prefixes,
    list_named_graphs,
    validate_sparql_query,
)

mcp = FastMCP("mcp-sparql")

MAX_DISPLAY_ROWS = 100

COMMON_PREFIXES = {
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "owl": "http://www.w3.org/2002/07/owl#",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "foaf": "http://xmlns.com/foaf/0.1/",
    "dc": "http://purl.org/dc/elements/1.1/",
    "dcterms": "http://purl.org/dc/terms/",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "schema": "https://schema.org/",
    "wd": "http://www.wikidata.org/entity/",
    "wdt": "http://www.wikidata.org/prop/direct/",
    "wdtn": "http://www.wikidata.org/prop/direct-normalized/",
    "p": "http://www.wikidata.org/prop/",
    "ps": "http://www.wikidata.org/prop/statement/",
    "psn": "http://www.wikidata.org/prop/statement/value-normalized/",
    "pq": "http://www.wikidata.org/qualifier/",
    "dbpedia": "http://dbpedia.org/resource/",
    "dbp": "http://dbpedia.org/property/",
    "dbr": "http://dbpedia.org/resource/",
    "dbo": "http://dbpedia.org/ontology/",
}


def _format_select_table(
    results: dict[str, Any], max_rows: int = MAX_DISPLAY_ROWS
) -> str:
    """Format SPARQL SELECT results as a Markdown table.

    Args:
        results: Parsed SPARQL JSON results.
        max_rows: Maximum rows to display.

    Returns:
        Formatted Markdown table string.
    """
    bindings = results.get("results", {}).get("bindings", [])
    if not bindings:
        return "No results found."

    variables = list(bindings[0].keys())
    total = len(bindings)
    display_bindings = bindings[:max_rows]
    rows = [_format_table_row(b, variables) for b in display_bindings]
    header = "| " + " | ".join(f"`{v}`" for v in variables) + " |"
    separator = "| " + " | ".join("---" for _ in variables) + " |"
    table = "\n".join([header, separator] + rows)
    if total > max_rows:
        table += f"\n\n*Showing {max_rows} of {total} results. Use `json` format or increase `max_rows` to see all.*"
    return table


def _format_table_row(binding: dict[str, Any], variables: list[str]) -> str:
    """Format a single SPARQL result binding as a table row.

    Args:
        binding: A single result binding dictionary.
        variables: List of variable names.

    Returns:
        Formatted Markdown table row string.
    """
    cells = []
    for v in variables:
        val = binding.get(v, {})
        value = val.get("value", "")
        dtype = val.get("datatype", "")
        if dtype:
            cells.append(f"`{value}` ({dtype.split('#')[-1]})")
        else:
            cells.append(f"`{value}`")
    return "| " + " | ".join(cells) + " |"


def _format_select_json(
    results: dict[str, Any], max_rows: int = MAX_DISPLAY_ROWS
) -> str:
    """Format SPARQL SELECT results as JSON.

    Args:
        results: Parsed SPARQL JSON results.
        max_rows: Maximum rows to include.

    Returns:
        Formatted JSON string.
    """
    bindings = results.get("results", {}).get("bindings", [])
    if not bindings:
        return json.dumps({"results": [], "total": 0})

    total = len(bindings)
    display_bindings = bindings[:max_rows]
    output = []
    for b in display_bindings:
        row = {}
        for k, v in b.items():
            row[k] = {"value": v.get("value", ""), "type": v.get("type", "")}
            if "datatype" in v:
                row[k]["datatype"] = v["datatype"]
        output.append(row)

    return json.dumps(
        {"results": output, "total": total, "showing": min(total, max_rows)}, indent=2
    )


def _format_rdf_graph(graph: Graph, output_format: RDFOutputFormat) -> str:
    """Format an RDF graph as Turtle or JSON.

    Args:
        graph: rdflib Graph object.
        output_format: Desired output format.

    Returns:
        Formatted RDF string.
    """
    if len(graph) == 0:
        return "No triples found."

    if output_format == RDFOutputFormat.TURTLE:
        return graph.serialize(format="turtle")

    data = []
    for s, p, o in graph:
        data.append({"subject": str(s), "predicate": str(p), "object": str(o)})
    return json.dumps(data, indent=2)


def _handle_error(e: Exception) -> str:
    """Format exception into a user-friendly error message.

    Args:
        e: The caught exception.

    Returns:
        Error message string.
    """
    if isinstance(e, httpx.HTTPStatusError):
        status = e.response.status_code
        if status == 401:
            return "Error: Authentication required. Provide valid credentials via the `headers` parameter."
        if status == 403:
            return "Error: Access denied. You don't have permission to query this endpoint."
        if status == 404:
            return "Error: Endpoint not found. Please verify the SPARQL endpoint URL."
        if status == 429:
            return (
                "Error: Rate limit exceeded. Please wait before making more requests."
            )
        if status >= 500:
            return f"Error: Server error (HTTP {status}). The endpoint may be temporarily unavailable."
        return f"Error: HTTP {status} — {e.response.text[:500]}"
    if isinstance(e, httpx.TimeoutException):
        return f"Error: Query timed out after {type(e).__name__}. Try increasing the timeout."
    if isinstance(e, httpx.ConnectError):
        return "Error: Could not connect to the endpoint. Verify the URL and your network connection."
    return f"Error: {type(e).__name__}: {e}"


@mcp.tool(
    name="sparql_query",
    annotations={
        "title": "Execute SPARQL SELECT Query",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def sparql_query(params: SparqlQueryInput) -> str:
    """Execute a SPARQL SELECT query against a SPARQL endpoint.

    Runs a SELECT query and returns results as a Markdown table or JSON array.
    Supports custom HTTP headers for authenticated endpoints.
    For long-running queries (large datasets, complex joins), increase the
    timeout parameter — default is 30s, maximum is 3600s (1 hour).

    Args:
        params: Query parameters including endpoint URL, SPARQL query, timeout,
            output format, optional headers, and max rows limit.

    Returns:
        Query results formatted as a Markdown table or JSON string.

    Examples:
        >>> # Query Wikidata for items
        >>> sparql_query(SparqlQueryInput(
        ...     endpoint="https://query.wikidata.org/sparql",
        ...     query="SELECT ?item ?itemLabel WHERE { ?item wdt:P31 wd:Q5 . ?item rdfs:label ?itemLabel . FILTER(LANG(?itemLabel) = 'en') } LIMIT 5"
        ... ))
        "| `item` | `itemLabel` |\n| --- | --- |\n| `http://www.wikidata.org/entity/Q5` | `human` |\n..."

        >>> # Query with authentication
        >>> sparql_query(SparqlQueryInput(
        ...     endpoint="https://my-endpoint.example.com/sparql",
        ...     query="SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 10",
        ...     headers={"Authorization": "Bearer my-token"}
        ... ))
    """
    try:
        result = await execute_sparql_select(
            endpoint=params.endpoint,
            query=params.query,
            timeout=params.timeout,
            headers=params.headers,
        )
        if params.output_format == OutputFormat.TABLE:
            return _format_select_table(result, params.max_rows)
        return _format_select_json(result, params.max_rows)
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="sparql_ask",
    annotations={
        "title": "Execute SPARQL ASK Query",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def sparql_ask(params: SparqlAskInput) -> str:
    """Execute a SPARQL ASK query and return a boolean result.

    ASK queries test whether a pattern exists in the data, returning true or false.

    Args:
        params: Query parameters including endpoint URL, SPARQL ASK query, timeout,
            and optional headers.

    Returns:
        "true" if the pattern exists, "false" otherwise.

    Examples:
        >>> # Check if a specific item exists
        >>> sparql_ask(SparqlAskInput(
        ...     endpoint="https://query.wikidata.org/sparql",
        ...     query="ASK { wd:Q42 wdt:P31 wd:Q5 }"
        ... ))
        "true"

        >>> # Check if a relationship exists
        >>> sparql_ask(SparqlAskInput(
        ...     endpoint="https://query.wikidata.org/sparql",
        ...     query="ASK { wd:Q42 wdt:P27 wd:Q142 }"
        ... ))
        "true"
    """
    try:
        result = await execute_sparql_ask(
            endpoint=params.endpoint,
            query=params.query,
            timeout=params.timeout,
            headers=params.headers,
        )
        return str(result).lower()
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="sparql_construct",
    annotations={
        "title": "Execute SPARQL CONSTRUCT Query",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def sparql_construct(params: SparqlConstructInput) -> str:
    """Execute a SPARQL CONSTRUCT query and return RDF triples.

    CONSTRUCT queries build an RDF graph from a template pattern.
    Results are returned as Turtle RDF or JSON-LD.
    For large-scale graph construction, increase the timeout parameter —
    default is 30s, maximum is 3600s (1 hour).

    Args:
        params: Query parameters including endpoint URL, SPARQL CONSTRUCT query,
            timeout, output format, optional headers, and max rows limit.

    Returns:
        RDF triples formatted as Turtle or JSON.

    Examples:
        >>> # Construct a subgraph
        >>> sparql_construct(SparqlConstructInput(
        ...     endpoint="https://query.wikidata.org/sparql",
        ...     query="CONSTRUCT { wd:Q42 rdfs:label ?name } WHERE { wd:Q42 rdfs:label ?name . FILTER(LANG(?name) = 'en') }"
        ... ))
        "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\\n..."
    """
    try:
        graph = await execute_sparql_construct(
            endpoint=params.endpoint,
            query=params.query,
            timeout=params.timeout,
            headers=params.headers,
        )
        if len(graph) > params.max_rows:
            limited_graph = Graph()
            for i, triple in enumerate(graph):
                if i >= params.max_rows:
                    break
                limited_graph.add(triple)
            return _format_rdf_graph(limited_graph, params.output_format)
        return _format_rdf_graph(graph, params.output_format)
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="sparql_describe",
    annotations={
        "title": "Execute SPARQL DESCRIBE Query",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def sparql_describe(params: SparqlDescribeInput) -> str:
    """Execute a SPARQL DESCRIBE query and return an RDF resource description.

    DESCRIBE queries return an RDF graph describing the specified resource(s).
    For resources with many properties, increase the timeout parameter —
    default is 30s, maximum is 3600s (1 hour).

    Args:
        params: Query parameters including endpoint URL, SPARQL DESCRIBE query,
            timeout, output format, optional headers, and max rows limit.

    Returns:
        RDF description formatted as Turtle or JSON.

    Examples:
        >>> # Describe a Wikidata entity
        >>> sparql_describe(SparqlDescribeInput(
        ...     endpoint="https://query.wikidata.org/sparql",
        ...     query="DESCRIBE wd:Q42"
        ... ))
        "@prefix ...> .\\n<...> ..."
    """
    try:
        graph = await execute_sparql_describe(
            endpoint=params.endpoint,
            query=params.query,
            timeout=params.timeout,
            headers=params.headers,
        )
        if len(graph) > params.max_rows:
            limited_graph = Graph()
            for i, triple in enumerate(graph):
                if i >= params.max_rows:
                    break
                limited_graph.add(triple)
            return _format_rdf_graph(limited_graph, params.output_format)
        return _format_rdf_graph(graph, params.output_format)
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="sparql_validate",
    annotations={
        "title": "Validate SPARQL Query Syntax",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def sparql_validate(params: SparqlValidateInput) -> str:
    """Validate SPARQL query syntax without executing it.

    Parses the query and reports whether it is syntactically valid.
    Useful for debugging query errors before running them against an endpoint.

    Args:
        params: Validation parameters containing the SPARQL query string.

    Returns:
        Validation result with status and error details if invalid.

    Examples:
        >>> # Valid query
        >>> sparql_validate(SparqlValidateInput(query="SELECT ?s WHERE { ?s ?p ?o }"))
        "Valid SPARQL query."

        >>> # Invalid query
        >>> sparql_validate(SparqlValidateInput(query="SELECT WHERE { }"))
        "Invalid SPARQL query: ..."
    """
    result = validate_sparql_query(params.query)
    if result["valid"]:
        return "Valid SPARQL query."
    return f"Invalid SPARQL query:\n{result['error']}"


@mcp.tool(
    name="sparql_list_graphs",
    annotations={
        "title": "List Named Graphs",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def sparql_list_graphs(params: SparqlListGraphsInput) -> str:
    """List available named graphs on a SPARQL endpoint.

    Queries the endpoint for all named graphs (contexts) available for querying.

    Args:
        params: Parameters including endpoint URL, timeout, and optional headers.

    Returns:
        List of named graph URIs.

    Examples:
        >>> sparql_list_graphs(SparqlListGraphsInput(
        ...     endpoint="https://query.wikidata.org/sparql"
        ... ))
        "Found 3 named graphs:\\n1. http://example.org/graph1\\n..."
    """
    try:
        graphs = await list_named_graphs(
            endpoint=params.endpoint,
            timeout=params.timeout,
            headers=params.headers,
        )
        if not graphs:
            return "No named graphs found on this endpoint."
        lines = [f"Found {len(graphs)} named graph(s):"]
        for i, g in enumerate(graphs, 1):
            lines.append(f"{i}. {g}")
        return "\n".join(lines)
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="sparql_get_prefixes",
    annotations={
        "title": "Get SPARQL Prefixes",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def sparql_get_prefixes(params: SparqlGetPrefixesInput) -> str:
    """Get commonly used prefixes for a SPARQL endpoint.

    Returns a combination of well-known standard prefixes (rdf, rdfs, owl, xsd, etc.)
    and any endpoint-specific prefixes discovered via the data.

    Args:
        params: Parameters including endpoint URL, timeout, and optional headers.

    Returns:
        Formatted list of prefix declarations for use in SPARQL queries.

    Examples:
        >>> sparql_get_prefixes(SparqlGetPrefixesInput(
        ...     endpoint="https://query.wikidata.org/sparql"
        ... ))
        "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\\n..."
    """
    try:
        endpoint_prefixes = await get_endpoint_prefixes(
            endpoint=params.endpoint,
            timeout=params.timeout,
            headers=params.headers,
        )
        all_prefixes = {**COMMON_PREFIXES, **endpoint_prefixes}
        lines = [f"PREFIX {k}: <{v}>" for k, v in sorted(all_prefixes.items())]
        return "\n".join(lines)
    except Exception as e:
        return _handle_error(e)


@mcp.resource("sparql://common-prefixes")
def get_common_prefixes() -> str:
    """Common SPARQL namespace prefixes.

    Returns a dictionary of standard namespace prefixes used in SPARQL queries,
    including RDF, RDFS, OWL, XSD, FOAF, Dublin Core, SKOS, Schema.org,
    Wikidata, and DBpedia.

    Returns:
        JSON string mapping prefix names to namespace URIs.
    """
    return json.dumps(COMMON_PREFIXES, indent=2)
