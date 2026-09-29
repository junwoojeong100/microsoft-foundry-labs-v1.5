"""Loopback-free stdio MCP server: synthetic read/draft functions, no external actions."""

from mcp.server.fastmcp import FastMCP

from workshop import get_stock as stock, prepare_purchase_request as draft

server = FastMCP("contoso-purchasing-v1")


@server.tool()
def get_stock(sku: str) -> dict:
    """Read Contoso synthetic stock; never change inventory."""
    return stock(sku)


@server.tool()
def prepare_purchase_request(sku: str, quantity: int) -> dict:
    """Prepare a draft only; never approve, order, pay or send messages."""
    return draft(sku, quantity)


if __name__ == "__main__":
    server.run(transport="stdio")
