"""HTTP client for executing SPARQL queries against endpoints."""

from __future__ import annotations

from typing import Any

import httpx
from rdflib import Graph
from rdflib.plugins.sparql.parser import parseQuery

USER_AGENT = "mcp-sparql/0.1.0 (https://github.com/daedalus/mcp-sparql)"


async def execute_sparql_select(
    endpoint: str,
    query: str,
    timeout: int = 30,
    headers: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Execute a SPARQL SELECT query and return parsed JSON results.

    Args:
        endpoint: SPARQL endpoint URL.
        query: SPARQL SELECT query string.
        timeout: Query timeout in seconds.
        headers: Optional HTTP headers.

    Returns:
        Parsed SPARQL JSON results dictionary.

    Raises:
        httpx.HTTPStatusError: If the endpoint returns an error status.
        httpx.TimeoutException: If the query times out.
    """
    default_headers = {
        "Accept": "application/sparql-results+json",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": USER_AGENT,
    }
    if headers:
        default_headers.update(headers)

    async with httpx.AsyncClient() as client:
        response = await client.post(
            endpoint,
            data={"query": query},
            headers=default_headers,
            timeout=float(timeout),
        )
        response.raise_for_status()
        return response.json()


async def execute_sparql_ask(
    endpoint: str,
    query: str,
    timeout: int = 30,
    headers: dict[str, str] | None = None,
) -> bool:
    """Execute a SPARQL ASK query and return a boolean result.

    Args:
        endpoint: SPARQL endpoint URL.
        query: SPARQL ASK query string.
        timeout: Query timeout in seconds.
        headers: Optional HTTP headers.

    Returns:
        Boolean result of the ASK query.

    Raises:
        httpx.HTTPStatusError: If the endpoint returns an error status.
        httpx.TimeoutException: If the query times out.
    """
    default_headers = {
        "Accept": "application/sparql-results+json",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": USER_AGENT,
    }
    if headers:
        default_headers.update(headers)

    async with httpx.AsyncClient() as client:
        response = await client.post(
            endpoint,
            data={"query": query},
            headers=default_headers,
            timeout=float(timeout),
        )
        response.raise_for_status()
        result = response.json()
        return result.get("boolean", False)


async def execute_sparql_construct(
    endpoint: str,
    query: str,
    timeout: int = 30,
    headers: dict[str, str] | None = None,
) -> Graph:
    """Execute a SPARQL CONSTRUCT query and return an RDF graph.

    Args:
        endpoint: SPARQL endpoint URL.
        query: SPARQL CONSTRUCT query string.
        timeout: Query timeout in seconds.
        headers: Optional HTTP headers.

    Returns:
        An rdflib Graph containing the constructed triples.

    Raises:
        httpx.HTTPStatusError: If the endpoint returns an error status.
        httpx.TimeoutException: If the query times out.
    """
    default_headers = {
        "Accept": "text/turtle",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": USER_AGENT,
    }
    if headers:
        default_headers.update(headers)

    async with httpx.AsyncClient() as client:
        response = await client.post(
            endpoint,
            data={"query": query},
            headers=default_headers,
            timeout=float(timeout),
        )
        response.raise_for_status()

    g = Graph()
    g.parse(data=response.text, format="turtle")
    return g


async def execute_sparql_describe(
    endpoint: str,
    query: str,
    timeout: int = 30,
    headers: dict[str, str] | None = None,
) -> Graph:
    """Execute a SPARQL DESCRIBE query and return an RDF graph.

    Args:
        endpoint: SPARQL endpoint URL.
        query: SPARQL DESCRIBE query string.
        timeout: Query timeout in seconds.
        headers: Optional HTTP headers.

    Returns:
        An rdflib Graph containing the described triples.

    Raises:
        httpx.HTTPStatusError: If the endpoint returns an error status.
        httpx.TimeoutException: If the query times out.
    """
    default_headers = {
        "Accept": "text/turtle",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": USER_AGENT,
    }
    if headers:
        default_headers.update(headers)

    async with httpx.AsyncClient() as client:
        response = await client.post(
            endpoint,
            data={"query": query},
            headers=default_headers,
            timeout=float(timeout),
        )
        response.raise_for_status()

    g = Graph()
    g.parse(data=response.text, format="turtle")
    return g


async def list_named_graphs(
    endpoint: str,
    timeout: int = 30,
    headers: dict[str, str] | None = None,
) -> list[str]:
    """List available named graphs on a SPARQL endpoint.

    Args:
        endpoint: SPARQL endpoint URL.
        timeout: Query timeout in seconds.
        headers: Optional HTTP headers.

    Returns:
        List of named graph URIs.

    Raises:
        httpx.HTTPStatusError: If the endpoint returns an error status.
        httpx.TimeoutException: If the query times out.
    """
    query = "SELECT ?g WHERE { GRAPH ?g {} }"
    result = await execute_sparql_select(endpoint, query, timeout, headers)
    bindings = result.get("results", {}).get("bindings", [])
    return [b["g"]["value"] for b in bindings if "g" in b]


async def get_endpoint_prefixes(
    endpoint: str,
    timeout: int = 30,
    headers: dict[str, str] | None = None,
) -> dict[str, str]:
    """Fetch commonly used prefixes from a SPARQL endpoint.

    Args:
        endpoint: SPARQL endpoint URL.
        timeout: Query timeout in seconds.
        headers: Optional HTTP headers.

    Returns:
        Dictionary mapping prefix names to namespace URIs.

    Raises:
        httpx.HTTPStatusError: If the endpoint returns an error status.
        httpx.TimeoutException: If the query times out.
    """
    query = """
    SELECT ?prefix ?iri WHERE {
      ?iri a <http://www.w3.org/2002/07/owl#Ontology> .
      ?iri <http://www.w3.org/2000/01/rdf-schema#label> ?prefix .
    } LIMIT 50
    """
    try:
        result = await execute_sparql_select(endpoint, query, timeout, headers)
        bindings = result.get("results", {}).get("bindings", [])
        prefixes = {}
        for b in bindings:
            if "prefix" in b and "iri" in b:
                prefixes[b["prefix"]["value"]] = b["iri"]["value"]
        return prefixes
    except Exception:
        return {}


def validate_sparql_query(query: str) -> dict[str, Any]:
    """Validate SPARQL query syntax without executing it.

    Args:
        query: SPARQL query string to validate.

    Returns:
        Dictionary with 'valid' boolean and optional 'error' message.
    """
    try:
        parseQuery(query)
        return {"valid": True, "error": None}
    except Exception as e:
        return {"valid": False, "error": str(e)}
