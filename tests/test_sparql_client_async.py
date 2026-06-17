"""Tests for mcp_sparql.core.sparql_client async functions (mocked HTTP)."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mcp_sparql.core.sparql_client import (
    execute_sparql_ask,
    execute_sparql_construct,
    execute_sparql_describe,
    execute_sparql_select,
    get_endpoint_prefixes,
    list_named_graphs,
)


@pytest.mark.asyncio
class TestExecuteSparqlSelect:
    """Tests for execute_sparql_select."""

    async def test_successful_query(self) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": {
                "bindings": [{"item": {"value": "http://example.org/a", "type": "uri"}}]
            }
        }
        mock_response.raise_for_status = MagicMock()
        with patch("mcp_sparql.core.sparql_client.httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.post.return_value = mock_response
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value = mock_instance
            result = await execute_sparql_select(
                "https://example.com/sparql",
                "SELECT ?item WHERE { ?item ?p ?o }",
            )
            assert "results" in result
            assert len(result["results"]["bindings"]) == 1

    async def test_with_headers(self) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": {"bindings": []}}
        mock_response.raise_for_status = MagicMock()
        with patch("mcp_sparql.core.sparql_client.httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.post.return_value = mock_response
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value = mock_instance
            await execute_sparql_select(
                "https://example.com/sparql",
                "SELECT ?s WHERE { ?s ?p ?o }",
                headers={"Authorization": "Bearer token"},
            )
            call_kwargs = mock_instance.post.call_args
            assert "Authorization" in call_kwargs[1]["headers"]


@pytest.mark.asyncio
class TestExecuteSparqlAsk:
    """Tests for execute_sparql_ask."""

    async def test_ask_true(self) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {"boolean": True}
        mock_response.raise_for_status = MagicMock()
        with patch("mcp_sparql.core.sparql_client.httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.post.return_value = mock_response
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value = mock_instance
            result = await execute_sparql_ask(
                "https://example.com/sparql",
                "ASK { ?s ?p ?o }",
            )
            assert result is True

    async def test_ask_false(self) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {"boolean": False}
        mock_response.raise_for_status = MagicMock()
        with patch("mcp_sparql.core.sparql_client.httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.post.return_value = mock_response
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value = mock_instance
            result = await execute_sparql_ask(
                "https://example.com/sparql",
                "ASK { ?s ?p ?o }",
            )
            assert result is False


@pytest.mark.asyncio
class TestExecuteSparqlConstruct:
    """Tests for execute_sparql_construct."""

    async def test_construct_with_triples(self) -> None:
        turtle_data = """
        @prefix ex: <http://example.org/> .
        ex:alice ex:name "Alice" .
        """
        mock_response = MagicMock()
        mock_response.text = turtle_data
        mock_response.raise_for_status = MagicMock()
        with patch("mcp_sparql.core.sparql_client.httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.post.return_value = mock_response
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value = mock_instance
            graph = await execute_sparql_construct(
                "https://example.com/sparql",
                "CONSTRUCT { ?s ?p ?o } WHERE { ?s ?p ?o }",
            )
            assert len(graph) == 1


@pytest.mark.asyncio
class TestExecuteSparqlDescribe:
    """Tests for execute_sparql_describe."""

    async def test_describe_with_triples(self) -> None:
        turtle_data = """
        @prefix ex: <http://example.org/> .
        ex:alice ex:name "Alice" .
        """
        mock_response = MagicMock()
        mock_response.text = turtle_data
        mock_response.raise_for_status = MagicMock()
        with patch("mcp_sparql.core.sparql_client.httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.post.return_value = mock_response
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value = mock_instance
            graph = await execute_sparql_describe(
                "https://example.com/sparql",
                "DESCRIBE <http://example.org/alice>",
            )
            assert len(graph) == 1


@pytest.mark.asyncio
class TestListNamedGraphs:
    """Tests for list_named_graphs."""

    async def test_list_graphs(self) -> None:
        mock_result = {
            "results": {
                "bindings": [
                    {"g": {"value": "http://example.org/graph1"}},
                    {"g": {"value": "http://example.org/graph2"}},
                ]
            }
        }
        with patch(
            "mcp_sparql.core.sparql_client.execute_sparql_select",
            new_callable=AsyncMock,
            return_value=mock_result,
        ):
            graphs = await list_named_graphs("https://example.com/sparql")
            assert len(graphs) == 2
            assert "http://example.org/graph1" in graphs

    async def test_list_graphs_empty(self) -> None:
        mock_result = {"results": {"bindings": []}}
        with patch(
            "mcp_sparql.core.sparql_client.execute_sparql_select",
            new_callable=AsyncMock,
            return_value=mock_result,
        ):
            graphs = await list_named_graphs("https://example.com/sparql")
            assert graphs == []


@pytest.mark.asyncio
class TestGetEndpointPrefixes:
    """Tests for get_endpoint_prefixes."""

    async def test_get_prefixes(self) -> None:
        mock_result = {
            "results": {
                "bindings": [
                    {
                        "prefix": {"value": "ex"},
                        "iri": {"value": "http://example.org/"},
                    },
                ]
            }
        }
        with patch(
            "mcp_sparql.core.sparql_client.execute_sparql_select",
            new_callable=AsyncMock,
            return_value=mock_result,
        ):
            prefixes = await get_endpoint_prefixes("https://example.com/sparql")
            assert "ex" in prefixes
            assert prefixes["ex"] == "http://example.org/"

    async def test_get_prefixes_error(self) -> None:
        with patch(
            "mcp_sparql.core.sparql_client.execute_sparql_select",
            new_callable=AsyncMock,
            side_effect=ValueError("fail"),
        ):
            prefixes = await get_endpoint_prefixes("https://example.com/sparql")
            assert prefixes == {}
