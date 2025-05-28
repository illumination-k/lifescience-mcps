import logging
from typing import Final

from mcp.server.fastmcp import FastMCP

from .client import CellosaurusClient
from .models import CellosaurusCellLine, CellosaurusSearchResult

logger = logging.getLogger(__name__)

CELLOSAURUS_API_ENDPOINT: Final[str] = "https://api.cellosaurus.org"

mcp = FastMCP("Cellosaurus-MCP")


@mcp.tool("cellosaurus_search")
async def search_cell_lines(
    query: str,
    fields: list[str] | None = None,
    page: int = 1,
    page_size: int = 10,
) -> CellosaurusSearchResult:
    """
    Search for cell lines in the Cellosaurus database.

    This function allows searching for cell lines using the Cellosaurus query syntax.
    Search criteria are combined with an implicit AND operator.

    Example queries:
    - ox:sapiens (human cell lines)
    - derived-from-site:liver (cell lines from liver)
    - di:Hepatoblastoma (cell lines from hepatoblastoma patients)
    - category:"Cancer cell line" (cancer cell lines)

    Args:
        query: The search query string using Cellosaurus search syntax.
        fields: List of specific fields to return. If None, all fields are returned.
        page: Page number for pagination.
        page_size: Number of results per page.

    Returns:
        CellosaurusSearchResult: A container with search results and total count.
    """
    client = CellosaurusClient()
    return await client.search_cell_lines(
        query=query, fields=fields, page=page, page_size=page_size
    )


@mcp.tool("cellosaurus_get_cell_line")
async def get_cell_line(
    accession: str, fields: list[str] | None = None
) -> CellosaurusCellLine:
    """
    Get detailed information about a specific cell line by its accession number.

    Args:
        accession: The Cellosaurus accession number (e.g., "CVCL_0033").
        fields: List of specific fields to return. If None, all fields are returned.

    Returns:
        CellosaurusCellLine: Detailed information about the requested cell line.
    """
    client = CellosaurusClient()
    return await client.get_cell_line(accession=accession, fields=fields)


def serve() -> None:
    """
    Start the FastMCP server for Cellosaurus.
    """
    logger.info("Starting Cellosaurus-MCP server...")
    mcp.run()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    serve()
