import logging

from mcp.server.fastmcp import FastMCP

from pubmed_mcp import PubMedArticleResult, PubMedClient

logger = logging.getLogger(__name__)
mcp = FastMCP("PubMed")


@mcp.tool("search")
async def search(
    keyword: str,
    retmax: int = 30,
    date_start: str | None = None,
    date_end: str | None = None,
) -> PubMedArticleResult:
    """
    Search PubMed for articles matching the given keyword.

    Args:
        keyword (str): The search term to query PubMed.
        retmax (int): Maximum number of results to return.
        date_start (str, optional): Start date in format YYYY/MM/DD. Used for date range filter with [dp].
        date_end (str, optional): End date in format YYYY/MM/DD. Used for date range filter with [dp].

    Returns:
        PubMedArticleResult: List of PubMed articles matching the search.
    """
    result = await PubMedClient().asearch_articles(
        keyword, retmax=retmax, date_start=date_start, date_end=date_end
    )
    return result


def serve() -> None:
    """
    Start the FastMCP server for PubMed.
    """
    logger.info("Starting PubMed MCP server...")
    mcp.run()


if __name__ == "__main__":
    serve()
