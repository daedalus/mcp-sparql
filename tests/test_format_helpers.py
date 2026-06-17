"""Tests for mcp_sparql.server formatting helpers (coverage boost)."""

from __future__ import annotations

import json

from mcp_sparql.server import _format_rdf_graph


def test_format_rdf_graph_turtle() -> None:
    from rdflib import Graph, Literal, Namespace

    g = Graph()
    EX = Namespace("http://example.org/")
    g.add((EX.alice, EX.name, Literal("Alice")))
    result = _format_rdf_graph(g, "turtle")
    assert "Alice" in result
    assert "ex:" in result or "example.org" in result


def test_format_rdf_graph_json() -> None:
    from rdflib import Graph, Literal, Namespace

    g = Graph()
    EX = Namespace("http://example.org/")
    g.add((EX.alice, EX.name, Literal("Alice")))
    result = _format_rdf_graph(g, "json")
    parsed = json.loads(result)
    assert len(parsed) == 1
    assert parsed[0]["subject"] == "http://example.org/alice"


def test_format_rdf_graph_empty() -> None:
    from rdflib import Graph

    g = Graph()
    result = _format_rdf_graph(g, "turtle")
    assert "No triples found" in result
