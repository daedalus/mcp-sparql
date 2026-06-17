"""Tests for mcp_sparql.core.models."""

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


class TestSparqlQueryInput:
    """Tests for SparqlQueryInput model."""

    def test_valid_input(self) -> None:
        result = SparqlQueryInput(
            endpoint="https://query.wikidata.org/sparql",
            query="SELECT ?s WHERE { ?s ?p ?o }",
        )
        assert result.endpoint == "https://query.wikidata.org/sparql"
        assert result.query == "SELECT ?s WHERE { ?s ?p ?o }"
        assert result.timeout == 30
        assert result.output_format == OutputFormat.TABLE
        assert result.max_rows == 1000

    def test_custom_params(self) -> None:
        result = SparqlQueryInput(
            endpoint="https://example.com/sparql",
            query="SELECT ?x WHERE { ?x ?y ?z }",
            timeout=60,
            output_format=OutputFormat.JSON,
            headers={"Authorization": "Bearer token"},
            max_rows=500,
        )
        assert result.timeout == 60
        assert result.output_format == OutputFormat.JSON
        assert result.headers == {"Authorization": "Bearer token"}
        assert result.max_rows == 500

    def test_empty_endpoint_raises(self) -> None:
        with pytest.raises(ValidationError):
            SparqlQueryInput(endpoint="", query="SELECT ?s WHERE { ?s ?p ?o }")

    def test_empty_query_raises(self) -> None:
        with pytest.raises(ValidationError):
            SparqlQueryInput(endpoint="https://example.com/sparql", query="")

    def test_whitespace_stripped(self) -> None:
        result = SparqlQueryInput(
            endpoint="  https://example.com/sparql  ",
            query="  SELECT ?s WHERE { ?s ?p ?o }  ",
        )
        assert result.endpoint == "https://example.com/sparql"
        assert result.query == "SELECT ?s WHERE { ?s ?p ?o }"

    def test_timeout_bounds(self) -> None:
        with pytest.raises(ValidationError):
            SparqlQueryInput(
                endpoint="https://example.com/sparql",
                query="SELECT ?s WHERE { ?s ?p ?o }",
                timeout=0,
            )
        with pytest.raises(ValidationError):
            SparqlQueryInput(
                endpoint="https://example.com/sparql",
                query="SELECT ?s WHERE { ?s ?p ?o }",
                timeout=3601,
            )

    def test_max_rows_bounds(self) -> None:
        with pytest.raises(ValidationError):
            SparqlQueryInput(
                endpoint="https://example.com/sparql",
                query="SELECT ?s WHERE { ?s ?p ?o }",
                max_rows=0,
            )
        with pytest.raises(ValidationError):
            SparqlQueryInput(
                endpoint="https://example.com/sparql",
                query="SELECT ?s WHERE { ?s ?p ?o }",
                max_rows=10001,
            )

    def test_extra_fields_forbidden(self) -> None:
        with pytest.raises(ValidationError):
            SparqlQueryInput(
                endpoint="https://example.com/sparql",
                query="SELECT ?s WHERE { ?s ?p ?o }",
                extra_field="should fail",
            )


class TestSparqlAskInput:
    """Tests for SparqlAskInput model."""

    def test_valid_input(self) -> None:
        result = SparqlAskInput(
            endpoint="https://query.wikidata.org/sparql",
            query="ASK { wd:Q42 wdt:P31 wd:Q5 }",
        )
        assert result.endpoint == "https://query.wikidata.org/sparql"
        assert result.query == "ASK { wd:Q42 wdt:P31 wd:Q5 }"
        assert result.timeout == 30

    def test_empty_endpoint_raises(self) -> None:
        with pytest.raises(ValidationError):
            SparqlAskInput(endpoint="", query="ASK { ?s ?p ?o }")

    def test_empty_query_raises(self) -> None:
        with pytest.raises(ValidationError):
            SparqlAskInput(endpoint="https://example.com/sparql", query="")


class TestSparqlConstructInput:
    """Tests for SparqlConstructInput model."""

    def test_valid_input(self) -> None:
        result = SparqlConstructInput(
            endpoint="https://query.wikidata.org/sparql",
            query="CONSTRUCT { ?s ?p ?o } WHERE { ?s ?p ?o } LIMIT 10",
        )
        assert result.output_format == RDFOutputFormat.TURTLE
        assert result.max_rows == 1000

    def test_json_format(self) -> None:
        result = SparqlConstructInput(
            endpoint="https://example.com/sparql",
            query="CONSTRUCT { ?s ?p ?o } WHERE { ?s ?p ?o }",
            output_format=RDFOutputFormat.JSON,
        )
        assert result.output_format == RDFOutputFormat.JSON


class TestSparqlDescribeInput:
    """Tests for SparqlDescribeInput model."""

    def test_valid_input(self) -> None:
        result = SparqlDescribeInput(
            endpoint="https://query.wikidata.org/sparql",
            query="DESCRIBE wd:Q42",
        )
        assert result.endpoint == "https://query.wikidata.org/sparql"
        assert result.query == "DESCRIBE wd:Q42"


class TestSparqlValidateInput:
    """Tests for SparqlValidateInput model."""

    def test_valid_input(self) -> None:
        result = SparqlValidateInput(query="SELECT ?s WHERE { ?s ?p ?o }")
        assert result.query == "SELECT ?s WHERE { ?s ?p ?o }"

    def test_empty_query_raises(self) -> None:
        with pytest.raises(ValidationError):
            SparqlValidateInput(query="")


class TestSparqlListGraphsInput:
    """Tests for SparqlListGraphsInput model."""

    def test_valid_input(self) -> None:
        result = SparqlListGraphsInput(endpoint="https://example.com/sparql")
        assert result.endpoint == "https://example.com/sparql"
        assert result.timeout == 30


class TestSparqlGetPrefixesInput:
    """Tests for SparqlGetPrefixesInput model."""

    def test_valid_input(self) -> None:
        result = SparqlGetPrefixesInput(endpoint="https://example.com/sparql")
        assert result.endpoint == "https://example.com/sparql"
        assert result.timeout == 30
