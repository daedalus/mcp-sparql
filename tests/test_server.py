"""Tests for mcp_sparql.server formatting and error handling."""

from __future__ import annotations

import json

import pytest

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
from mcp_sparql.server import (
    _format_select_json,
    _format_select_table,
    _handle_error,
    get_common_prefixes,
)


class TestFormatSelectTable:
    """Tests for _format_select_table helper."""

    def test_empty_results(self) -> None:
        result = _format_select_table({"results": {"bindings": []}})
        assert result == "No results found."

    def test_single_row(self) -> None:
        results = {
            "results": {
                "bindings": [
                    {
                        "item": {"value": "http://example.org/a", "type": "uri"},
                        "label": {"value": "Example", "type": "literal"},
                    }
                ]
            }
        }
        output = _format_select_table(results)
        assert "Example" in output
        assert "http://example.org/a" in output
        assert "| `item` | `label` |" in output

    def test_multiple_rows(self) -> None:
        results = {
            "results": {
                "bindings": [
                    {"item": {"value": "a", "type": "uri"}},
                    {"item": {"value": "b", "type": "uri"}},
                ]
            }
        }
        output = _format_select_table(results)
        assert "| `a` |" in output
        assert "| `b` |" in output

    def test_truncation_message(self) -> None:
        bindings = [{"x": {"value": str(i)}} for i in range(5)]
        results = {"results": {"bindings": bindings}}
        output = _format_select_table(results, max_rows=3)
        assert "Showing 3 of 5 results" in output

    def test_datatype_shown(self) -> None:
        results = {
            "results": {
                "bindings": [
                    {
                        "val": {
                            "value": "42",
                            "datatype": "http://www.w3.org/2001/XMLSchema#integer",
                        }
                    }
                ]
            }
        }
        output = _format_select_table(results)
        assert "integer" in output


class TestFormatSelectJson:
    """Tests for _format_select_json helper."""

    def test_empty_results(self) -> None:
        result = _format_select_json({"results": {"bindings": []}})
        parsed = json.loads(result)
        assert parsed["results"] == []
        assert parsed["total"] == 0

    def test_single_row(self) -> None:
        results = {
            "results": {
                "bindings": [{"item": {"value": "http://example.org/a", "type": "uri"}}]
            }
        }
        output = _format_select_json(results)
        parsed = json.loads(output)
        assert len(parsed["results"]) == 1
        assert parsed["results"][0]["item"]["value"] == "http://example.org/a"

    def test_truncation(self) -> None:
        bindings = [{"x": {"value": str(i)}} for i in range(5)]
        results = {"results": {"bindings": bindings}}
        output = _format_select_json(results, max_rows=2)
        parsed = json.loads(output)
        assert parsed["showing"] == 2
        assert parsed["total"] == 5


class TestHandleError:
    """Tests for _handle_error helper."""

    def test_generic_exception(self) -> None:
        result = _handle_error(ValueError("test error"))
        assert "ValueError" in result
        assert "test error" in result

    def test_timeout_exception(self) -> None:
        import httpx

        result = _handle_error(httpx.TimeoutException("timeout"))
        assert "timed out" in result

    def test_connect_error(self) -> None:
        import httpx

        result = _handle_error(httpx.ConnectError("connection refused"))
        assert "Could not connect" in result


class TestGetCommonPrefixes:
    """Tests for get_common_prefixes resource."""

    def test_returns_json(self) -> None:
        result = get_common_prefixes()
        parsed = json.loads(result)
        assert "rdf" in parsed
        assert "rdfs" in parsed
        assert "owl" in parsed
        assert "xsd" in parsed
        assert "foaf" in parsed
        assert "schema" in parsed
        assert "wd" in parsed
        assert "dbpedia" in parsed
