"""Tests for mcp_sparql.core.sparql_client."""

from __future__ import annotations

import pytest

from mcp_sparql.core.sparql_client import validate_sparql_query


class TestValidateSparqlQuery:
    """Tests for validate_sparql_query function."""

    def test_valid_select_query(self) -> None:
        result = validate_sparql_query("SELECT ?s WHERE { ?s ?p ?o }")
        assert result["valid"] is True
        assert result["error"] is None

    def test_valid_ask_query(self) -> None:
        result = validate_sparql_query("ASK { ?s ?p ?o }")
        assert result["valid"] is True
        assert result["error"] is None

    def test_valid_construct_query(self) -> None:
        result = validate_sparql_query("CONSTRUCT { ?s ?p ?o } WHERE { ?s ?p ?o }")
        assert result["valid"] is True
        assert result["error"] is None

    def test_valid_describe_query(self) -> None:
        result = validate_sparql_query("DESCRIBE <http://example.org/resource>")
        assert result["valid"] is True
        assert result["error"] is None

    def test_valid_select_with_prefix(self) -> None:
        query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT ?s WHERE { ?s rdf:type ?o }
        """
        result = validate_sparql_query(query)
        assert result["valid"] is True

    def test_valid_select_with_filter(self) -> None:
        query = """
        SELECT ?item ?label WHERE {
            ?item <http://www.w3.org/2000/01/rdf-schema#label> ?label .
            FILTER(LANG(?label) = 'en')
        }
        """
        result = validate_sparql_query(query)
        assert result["valid"] is True

    def test_valid_select_with_optional(self) -> None:
        query = """
        SELECT ?s ?p ?o WHERE {
            ?s ?p ?o .
            OPTIONAL { ?s <http://example.org/name> ?name }
        }
        """
        result = validate_sparql_query(query)
        assert result["valid"] is True

    def test_valid_select_with_union(self) -> None:
        query = """
        SELECT ?s WHERE {
            { ?s a <http://example.org/Type1> } UNION { ?s a <http://example.org/Type2> }
        }
        """
        result = validate_sparql_query(query)
        assert result["valid"] is True

    def test_valid_select_with_limit_offset(self) -> None:
        query = "SELECT ?s WHERE { ?s ?p ?o } LIMIT 100 OFFSET 20"
        result = validate_sparql_query(query)
        assert result["valid"] is True

    def test_valid_select_with_order_by(self) -> None:
        query = "SELECT ?s ?name WHERE { ?s <http://example.org/name> ?name } ORDER BY ?name"
        result = validate_sparql_query(query)
        assert result["valid"] is True

    def test_valid_select_with_bindings(self) -> None:
        query = """
        SELECT ?s WHERE {
            VALUES ?s { <http://example.org/a> <http://example.org/b> }
            ?s ?p ?o .
        }
        """
        result = validate_sparql_query(query)
        assert result["valid"] is True

    def test_valid_select_with_subquery(self) -> None:
        query = """
        SELECT ?s ?count WHERE {
            ?s <http://example.org/name> ?name .
            {
                SELECT ?s (COUNT(?o) AS ?count) WHERE {
                    ?s ?p ?o .
                } GROUP BY ?s
            }
        }
        """
        result = validate_sparql_query(query)
        assert result["valid"] is True

    def test_invalid_query_syntax(self) -> None:
        result = validate_sparql_query("SELECT WHERE { }")
        assert result["valid"] is False
        assert result["error"] is not None

    def test_invalid_query_missing_braces(self) -> None:
        result = validate_sparql_query("SELECT ?s WHERE")
        assert result["valid"] is False
        assert result["error"] is not None

    def test_invalid_query_garbage(self) -> None:
        result = validate_sparql_query("this is not a sparql query at all")
        assert result["valid"] is False
        assert result["error"] is not None

    def test_empty_query_string(self) -> None:
        result = validate_sparql_query("")
        assert result["valid"] is False

    def test_valid_select_with_bindings_keyword(self) -> None:
        query = "SELECT ?s WHERE { ?s a <http://example.org/Thing> . }"
        result = validate_sparql_query(query)
        assert result["valid"] is True

    def test_valid_select_with_service(self) -> None:
        query = """
        SELECT ?s ?o WHERE {
            SERVICE <http://example.org/sparql> {
                ?s ?p ?o .
            }
        }
        """
        result = validate_sparql_query(query)
        assert result["valid"] is True

    def test_valid_select_with_values(self) -> None:
        query = """
        SELECT ?s WHERE {
            VALUES ?s { <http://example.org/a> }
            ?s ?p ?o .
        }
        """
        result = validate_sparql_query(query)
        assert result["valid"] is True

    def test_valid_select_with_group_by(self) -> None:
        query = """
        SELECT ?s (COUNT(?o) AS ?count) WHERE {
            ?s ?p ?o .
        } GROUP BY ?s
        """
        result = validate_sparql_query(query)
        assert result["valid"] is True

    def test_valid_select_with_having(self) -> None:
        query = """
        SELECT ?s (COUNT(?o) AS ?count) WHERE {
            ?s ?p ?o .
        } GROUP BY ?s HAVING (COUNT(?o) > 5)
        """
        result = validate_sparql_query(query)
        assert result["valid"] is True

    def test_valid_select_with_aggregate(self) -> None:
        query = """
        SELECT (COUNT(?s) AS ?total) WHERE {
            ?s a <http://example.org/Thing> .
        }
        """
        result = validate_sparql_query(query)
        assert result["valid"] is True
