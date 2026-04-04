"""MCP server for Steam gaming library, achievements, stats, and store search."""

from .server import mcp


def main():
    mcp.run(transport="stdio")


__all__ = ["main", "mcp"]
