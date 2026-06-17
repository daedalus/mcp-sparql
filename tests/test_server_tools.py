"""Tests for mcp_sparql.server tool functions (mocked HTTP)."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, patch

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
    sparql_ask,
    sparql_construct,
    sparql_describe,
    sparql_get_prefixes,
    sparql_list_graphs,
    sparql_query,
    sparql_validate,
)


@pytest.mark.asyncio
class TestSparqlQueryTool:
    """Tests for sparql_query tool."""

    async def test_select_table_format(self) -> None:
        mock_response = {
            "results": {
                "bindings": [
                    {
                        "item": {"value": "http://example.org/a", "type": "uri"},
                        "label": {"value": "Alice", "type": "literal"},
                    }
                ]
            }
        }
        with patch(
            "mcp_sparql.server.execute_sparql_select",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            result = await sparql_query(
                SparqlQueryInput(
                    endpoint="https://example.com/sparql",
                    query="SELECT ?item ?label WHERE { ?item rdfs:label ?label }",
                )
            )
            assert "Alice" in result
            assert "http://example.org/a" in result

    async def test_select_json_format(self) -> None:
        mock_response = {
            "results": {
                "bindings": [{"item": {"value": "http://example.org/a", "type": "uri"}}]
            }
        }
        with patch(
            "mcp_sparql.server.execute_sparql_select",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            result = await sparql_query(
                SparqlQueryInput(
                    endpoint="https://example.com/sparql",
                    query="SELECT ?item WHERE { ?item ?p ?o }",
                    output_format=OutputFormat.JSON,
                )
            )
            parsed = json.loads(result)
            assert "results" in parsed
            assert len(parsed["results"]) == 1

    async def test_empty_results(self) -> None:
        mock_response = {"results": {"bindings": []}}
        with patch(
            "mcp_sparql.server.execute_sparql_select",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            result = await sparql_query(
                SparqlQueryInput(
                    endpoint="https://example.com/sparql",
                    query="SELECT ?s WHERE { ?s ?p ?o }",
                )
            )
            assert "No results found" in result

    async def test_error_handling(self) -> None:
        with patch(
            "mcp_sparql.server.execute_sparql_select",
            new_callable=AsyncMock,
            side_effect=ValueError("test error"),
        ):
            result = await sparql_query(
                SparqlQueryInput(
                    endpoint="https://example.com/sparql",
                    query="SELECT ?s WHERE { ?s ?p ?o }",
                )
            )
            assert "Error" in result


@pytest.mark.asyncio
class TestSparqlAskTool:
    """Tests for sparql_ask tool."""

    async def test_ask_true(self) -> None:
        with patch(
            "mcp_sparql.server.execute_sparql_ask",
            new_callable=AsyncMock,
            return_value=True,
        ):
            result = await sparql_ask(
                SparqlAskInput(
                    endpoint="https://example.com/sparql",
                    query="ASK { ?s ?p ?o }",
                )
            )
            assert result == "true"

    async def test_ask_false(self) -> None:
        with patch(
            "mcp_sparql.server.execute_sparql_ask",
            new_callable=AsyncMock,
            return_value=False,
        ):
            result = await sparql_ask(
                SparqlAskInput(
                    endpoint="https://example.com/sparql",
                    query="ASK { ?s ?p ?o }",
                )
            )
            assert result == "false"

    async def test_ask_error(self) -> None:
        with patch(
            "mcp_sparql.server.execute_sparql_ask",
            new_callable=AsyncMock,
            side_effect=ValueError("fail"),
        ):
            result = await sparql_ask(
                SparqlAskInput(
                    endpoint="https://example.com/sparql",
                    query="ASK { ?s ?p ?o }",
                )
            )
            assert "Error" in result


@pytest.mark.asyncio
class TestSparqlConstructTool:
    """Tests for sparql_construct tool."""

    async def test_construct_turtle(self) -> None:
        from rdflib import Graph, Literal, Namespace, URIRef

        g = Graph()
        EX = Namespace("http://example.org/")
        g.add((EX.alice, EX.name, Literal("Alice")))
        with patch(
            "mcp_sparql.server.execute_sparql_construct",
            new_callable=AsyncMock,
            return_value=g,
        ):
            result = await sparql_construct(
                SparqlConstructInput(
                    endpoint="https://example.com/sparql",
                    query="CONSTRUCT { ?s ?p ?o } WHERE { ?s ?p ?o }",
                )
            )
            assert "Alice" in result

    async def test_construct_json(self) -> None:
        from rdflib import Graph, Literal, Namespace

        g = Graph()
        EX = Namespace("http://example.org/")
        g.add((EX.alice, EX.name, Literal("Alice")))
        with patch(
            "mcp_sparql.server.execute_sparql_construct",
            new_callable=AsyncMock,
            return_value=g,
        ):
            result = await sparql_construct(
                SparqlConstructInput(
                    endpoint="https://example.com/sparql",
                    query="CONSTRUCT { ?s ?p ?o } WHERE { ?s ?p ?o }",
                    output_format=RDFOutputFormat.JSON,
                )
            )
            parsed = json.loads(result)
            assert len(parsed) == 1
            assert parsed[0]["subject"] == "http://example.org/alice"

    async def test_construct_empty(self) -> None:
        from rdflib import Graph

        g = Graph()
        with patch(
            "mcp_sparql.server.execute_sparql_construct",
            new_callable=AsyncMock,
            return_value=g,
        ):
            result = await sparql_construct(
                SparqlConstructInput(
                    endpoint="https://example.com/sparql",
                    query="CONSTRUCT { ?s ?p ?o } WHERE { ?s ?p ?o }",
                )
            )
            assert "No triples found" in result

    async def test_construct_truncation(self) -> None:
        from rdflib import Graph, Literal, Namespace

        g = Graph()
        EX = Namespace("http://example.org/")
        for i in range(5):
            g.add((EX[f"item{i}"], EX.name, Literal(f"Item {i}")))
        with patch(
            "mcp_sparql.server.execute_sparql_construct",
            new_callable=AsyncMock,
            return_value=g,
        ):
            result = await sparql_construct(
                SparqlConstructInput(
                    endpoint="https://example.com/sparql",
                    query="CONSTRUCT { ?s ?p ?o } WHERE { ?s ?p ?o }",
                    max_rows=2,
                )
            )
            assert "Item" in result
            assert "Item 4" not in result or result.count("Item") == 2

    async def test_construct_error(self) -> None:
        with patch(
            "mcp_sparql.server.execute_sparql_construct",
            new_callable=AsyncMock,
            side_effect=ValueError("fail"),
        ):
            result = await sparql_construct(
                SparqlConstructInput(
                    endpoint="https://example.com/sparql",
                    query="CONSTRUCT { ?s ?p ?o } WHERE { ?s ?p ?o }",
                )
            )
            assert "Error" in result


@pytest.mark.asyncio
class TestSparqlDescribeTool:
    """Tests for sparql_describe tool."""

    async def test_describe_turtle(self) -> None:
        from rdflib import Graph, Literal, Namespace

        g = Graph()
        EX = Namespace("http://example.org/")
        g.add((EX.alice, EX.name, Literal("Alice")))
        with patch(
            "mcp_sparql.server.execute_sparql_describe",
            new_callable=AsyncMock,
            return_value=g,
        ):
            result = await sparql_describe(
                SparqlDescribeInput(
                    endpoint="https://example.com/sparql",
                    query="DESCRIBE <http://example.org/alice>",
                )
            )
            assert "Alice" in result

    async def test_describe_empty(self) -> None:
        from rdflib import Graph

        g = Graph()
        with patch(
            "mcp_sparql.server.execute_sparql_describe",
            new_callable=AsyncMock,
            return_value=g,
        ):
            result = await sparql_describe(
                SparqlDescribeInput(
                    endpoint="https://example.com/sparql",
                    query="DESCRIBE <http://example.org/unknown>",
                )
            )
            assert "No triples found" in result

    async def test_describe_error(self) -> None:
        with patch(
            "mcp_sparql.server.execute_sparql_describe",
            new_callable=AsyncMock,
            side_effect=ValueError("fail"),
        ):
            result = await sparql_describe(
                SparqlDescribeInput(
                    endpoint="https://example.com/sparql",
                    query="DESCRIBE <http://example.org/alice>",
                )
            )
            assert "Error" in result


@pytest.mark.asyncio
class TestSparqlValidateTool:
    """Tests for sparql_validate tool."""

    async def test_valid_query(self) -> None:
        result = await sparql_validate(
            SparqlValidateInput(
                query="SELECT ?s WHERE { ?s ?p ?o }",
            )
        )
        assert "Valid" in result

    async def test_invalid_query(self) -> None:
        result = await sparql_validate(
            SparqlValidateInput(
                query="SELECT WHERE { }",
            )
        )
        assert "Invalid" in result


@pytest.mark.asyncio
class TestSparqlListGraphsTool:
    """Tests for sparql_list_graphs tool."""

    async def test_list_graphs(self) -> None:
        with patch(
            "mcp_sparql.server.list_named_graphs",
            new_callable=AsyncMock,
            return_value=["http://g1", "http://g2"],
        ):
            result = await sparql_list_graphs(
                SparqlListGraphsInput(
                    endpoint="https://example.com/sparql",
                )
            )
            assert "2 named graph" in result
            assert "http://g1" in result
            assert "http://g2" in result

    async def test_list_graphs_empty(self) -> None:
        with patch(
            "mcp_sparql.server.list_named_graphs",
            new_callable=AsyncMock,
            return_value=[],
        ):
            result = await sparql_list_graphs(
                SparqlListGraphsInput(
                    endpoint="https://example.com/sparql",
                )
            )
            assert "No named graphs" in result

    async def test_list_graphs_error(self) -> None:
        with patch(
            "mcp_sparql.server.list_named_graphs",
            new_callable=AsyncMock,
            side_effect=ValueError("fail"),
        ):
            result = await sparql_list_graphs(
                SparqlListGraphsInput(
                    endpoint="https://example.com/sparql",
                )
            )
            assert "Error" in result


@pytest.mark.asyncio
class TestSparqlGetPrefixesTool:
    """Tests for sparql_get_prefixes tool."""

    async def test_get_prefixes(self) -> None:
        with patch(
            "mcp_sparql.server.get_endpoint_prefixes",
            new_callable=AsyncMock,
            return_value={"ex": "http://example.org/"},
        ):
            result = await sparql_get_prefixes(
                SparqlGetPrefixesInput(
                    endpoint="https://example.com/sparql",
                )
            )
            assert "PREFIX rdf:" in result
            assert "PREFIX ex:" in result

    async def test_get_prefixes_error(self) -> None:
        with patch(
            "mcp_sparql.server.get_endpoint_prefixes",
            new_callable=AsyncMock,
            side_effect=ValueError("fail"),
        ):
            result = await sparql_get_prefixes(
                SparqlGetPrefixesInput(
                    endpoint="https://example.com/sparql",
                )
            )
            assert "Error" in result
