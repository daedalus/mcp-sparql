# AGENTS.md — mcp-sparql

## Overview

An MCP server that exposes SPARQL query functionalities, enabling LLMs to query RDF triple stores (Wikidata, DBpedia, custom endpoints) via the Model Context Protocol. Supports SELECT, ASK, CONSTRUCT, and DESCRIBE queries, query validation, named graph listing, and prefix discovery.

## Commands

| Command | Description |
|---------|------------|
| `pytest` | Run test suite |
| `ruff format` | Format code |
| `mdformat` | Format markdown |
| `prospector --with-tool ruff --with-tool mypy --with-tool pylint src/` | Lint + type check |
| `opengrep --config=auto --severity=ERROR src/` | Security scanning |
| `vulture --min-confidence 90 src/` | Dead code detection |
| `lizard src/ --min-cyclomatic-complexity 10` | Code complexity analysis |

## Development

```bash
# Setup
pip install -e ".[test]"

# Test
pytest

# Format
ruff format src/ tests/

# Lint
prospector --with-tool ruff --with-tool mypy --with-tool pylint src/
```

## Testing

Uses pytest with pytest-cov for coverage. Tests cover:

- Pydantic model validation (all edge cases)
- SPARQL query syntax validation
- Table/JSON formatting helpers
- Error handling paths
- Resource endpoints

## Code Style

- Format: ruff format
- Lint + Type check: prospector (ruff check + mypy + pylint)
- Docstrings: Google style

## Release

```bash
./tools/release.sh          # bump patch (default)
./tools/release.sh minor
./tools/release.sh major
```

## MCP Server

```bash
pip install mcp-sparql
```

Add to `mcp.json`:

```json
{
  "mcpServers": {
    "mcp-sparql": {
      "command": "mcp-sparql"
    }
  }
}
```
