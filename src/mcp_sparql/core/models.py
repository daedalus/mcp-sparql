"""Data models for mcp-sparql."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class OutputFormat(str, Enum):
    """Output format for SPARQL query results."""

    TABLE = "table"
    JSON = "json"


class RDFOutputFormat(str, Enum):
    """Output format for RDF results (CONSTRUCT/DESCRIBE)."""

    TURTLE = "turtle"
    JSON = "json"


class SparqlQueryInput(BaseModel):
    """Input model for SPARQL SELECT queries."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    endpoint: str = Field(
        ...,
        description="SPARQL endpoint URL (e.g., 'https://query.wikidata.org/sparql')",
        min_length=1,
    )
    query: str = Field(
        ...,
        description="SPARQL SELECT query to execute",
        min_length=1,
    )
    timeout: int = Field(
        default=30,
        description="Query timeout in seconds (increase for large datasets or complex queries)",
        ge=1,
        le=3600,
    )
    output_format: OutputFormat = Field(
        default=OutputFormat.TABLE,
        description="Output format: 'table' for Markdown table, 'json' for JSON array",
    )
    headers: dict[str, str] | None = Field(
        default=None,
        description="Optional HTTP headers (e.g., {'Authorization': 'Bearer token'})",
    )
    max_rows: int = Field(
        default=1000,
        description="Maximum number of result rows to return",
        ge=1,
        le=10000,
    )


class SparqlAskInput(BaseModel):
    """Input model for SPARQL ASK queries."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    endpoint: str = Field(
        ...,
        description="SPARQL endpoint URL",
        min_length=1,
    )
    query: str = Field(
        ...,
        description="SPARQL ASK query to execute",
        min_length=1,
    )
    timeout: int = Field(
        default=30,
        description="Query timeout in seconds (increase for large datasets or complex queries)",
        ge=1,
        le=3600,
    )
    headers: dict[str, str] | None = Field(
        default=None,
        description="Optional HTTP headers",
    )


class SparqlConstructInput(BaseModel):
    """Input model for SPARQL CONSTRUCT queries."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    endpoint: str = Field(
        ...,
        description="SPARQL endpoint URL",
        min_length=1,
    )
    query: str = Field(
        ...,
        description="SPARQL CONSTRUCT query to execute",
        min_length=1,
    )
    timeout: int = Field(
        default=30,
        description="Query timeout in seconds (increase for large datasets or complex queries)",
        ge=1,
        le=3600,
    )
    output_format: RDFOutputFormat = Field(
        default=RDFOutputFormat.TURTLE,
        description="Output format: 'turtle' for Turtle RDF, 'json' for JSON-LD",
    )
    headers: dict[str, str] | None = Field(
        default=None,
        description="Optional HTTP headers",
    )
    max_rows: int = Field(
        default=1000,
        description="Maximum number of triples to return",
        ge=1,
        le=10000,
    )


class SparqlDescribeInput(BaseModel):
    """Input model for SPARQL DESCRIBE queries."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    endpoint: str = Field(
        ...,
        description="SPARQL endpoint URL",
        min_length=1,
    )
    query: str = Field(
        ...,
        description="SPARQL DESCRIBE query to execute",
        min_length=1,
    )
    timeout: int = Field(
        default=30,
        description="Query timeout in seconds (increase for large datasets or complex queries)",
        ge=1,
        le=3600,
    )
    output_format: RDFOutputFormat = Field(
        default=RDFOutputFormat.TURTLE,
        description="Output format: 'turtle' for Turtle RDF, 'json' for JSON-LD",
    )
    headers: dict[str, str] | None = Field(
        default=None,
        description="Optional HTTP headers",
    )
    max_rows: int = Field(
        default=1000,
        description="Maximum number of triples to return",
        ge=1,
        le=10000,
    )


class SparqlValidateInput(BaseModel):
    """Input model for SPARQL query validation."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    query: str = Field(
        ...,
        description="SPARQL query to validate",
        min_length=1,
    )


class SparqlListGraphsInput(BaseModel):
    """Input model for listing named graphs."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    endpoint: str = Field(
        ...,
        description="SPARQL endpoint URL",
        min_length=1,
    )
    timeout: int = Field(
        default=30,
        description="Query timeout in seconds (increase for large datasets or complex queries)",
        ge=1,
        le=3600,
    )
    headers: dict[str, str] | None = Field(
        default=None,
        description="Optional HTTP headers",
    )


class SparqlGetPrefixesInput(BaseModel):
    """Input model for fetching endpoint prefixes."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    endpoint: str = Field(
        ...,
        description="SPARQL endpoint URL",
        min_length=1,
    )
    timeout: int = Field(
        default=30,
        description="Query timeout in seconds (increase for large datasets or complex queries)",
        ge=1,
        le=3600,
    )
    headers: dict[str, str] | None = Field(
        default=None,
        description="Optional HTTP headers",
    )
