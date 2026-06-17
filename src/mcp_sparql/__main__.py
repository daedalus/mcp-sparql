"""CLI entry point for mcp-sparql MCP server."""

from __future__ import annotations

from mcp_sparql.server import mcp


def main() -> int:
    """Run the mcp-sparql MCP server.

    Returns:
        Exit code (always 0).
    """
    mcp.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
