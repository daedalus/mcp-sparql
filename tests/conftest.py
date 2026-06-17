"""Shared test fixtures for mcp-sparql."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

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
from mcp_sparql.core.sparql_client import validate_sparql_query


@pytest.fixture
def sample_endpoint() -> str:
    """A sample SPARQL endpoint URL."""
    return "https://query.wikidata.org/sparql"


@pytest.fixture
def sample_select_query() -> str:
    """A sample SPARQL SELECT query."""
    return "SELECT ?item ?itemLabel WHERE { ?item wdt:P31 wd:Q5 . ?item rdfs:label ?itemLabel . FILTER(LANG(?itemLabel) = 'en') } LIMIT 5"


@pytest.fixture
def sample_ask_query() -> str:
    """A sample SPARQL ASK query."""
    return "ASK { wd:Q42 wdt:P31 wd:Q5 }"


@pytest.fixture
def sample_construct_query() -> str:
    """A sample SPARQL CONSTRUCT query."""
    return "CONSTRUCT { wd:Q42 rdfs:label ?name } WHERE { wd:Q42 rdfs:label ?name . FILTER(LANG(?name) = 'en') }"


@pytest.fixture
def sample_describe_query() -> str:
    """A sample SPARQL DESCRIBE query."""
    return "DESCRIBE wd:Q42"


@pytest.fixture
def valid_select_input(
    sample_endpoint: str, sample_select_query: str
) -> SparqlQueryInput:
    """A valid SELECT query input."""
    return SparqlQueryInput(endpoint=sample_endpoint, query=sample_select_query)


@pytest.fixture
def valid_ask_input(sample_endpoint: str, sample_ask_query: str) -> SparqlAskInput:
    """A valid ASK query input."""
    return SparqlAskInput(endpoint=sample_endpoint, query=sample_ask_query)


@pytest.fixture
def valid_construct_input(
    sample_endpoint: str, sample_construct_query: str
) -> SparqlConstructInput:
    """A valid CONSTRUCT query input."""
    return SparqlConstructInput(endpoint=sample_endpoint, query=sample_construct_query)


@pytest.fixture
def valid_describe_input(
    sample_endpoint: str, sample_describe_query: str
) -> SparqlDescribeInput:
    """A valid DESCRIBE query input."""
    return SparqlDescribeInput(endpoint=sample_endpoint, query=sample_describe_query)


@pytest.fixture
def valid_validate_input(sample_select_query: str) -> SparqlValidateInput:
    """A valid validate input."""
    return SparqlValidateInput(query=sample_select_query)


@pytest.fixture
def valid_list_graphs_input(sample_endpoint: str) -> SparqlListGraphsInput:
    """A valid list graphs input."""
    return SparqlListGraphsInput(endpoint=sample_endpoint)


@pytest.fixture
def valid_get_prefixes_input(sample_endpoint: str) -> SparqlGetPrefixesInput:
    """A valid get prefixes input."""
    return SparqlGetPrefixesInput(endpoint=sample_endpoint)
