import logging

from mcp.server.fastmcp import FastMCP

from pubmed_mcp import PubMedArticleResult, PubMedClient

logger = logging.getLogger(__name__)
mcp = FastMCP("PubMed")


@mcp.tool("pubmed_search")
async def search(
    keyword: str,
    retmax: int = 30,
    date_start: str | None = None,
    date_end: str | None = None,
    mesh_terms: list[str] | None = None,
    *,
    open_access: bool = False,
) -> PubMedArticleResult:
    """
    Search PubMed for articles matching the given keyword.

    Args:
        keyword (str): The search term to query PubMed.
        retmax (int): Maximum number of results to return.
        date_start (str, optional): Start date in format YYYY/MM/DD. Used for date range filter with [dp].
        date_end (str, optional): End date in format YYYY/MM/DD. Used for date range filter with [dp].
        mesh_terms (list[str], optional): List of MeSH terms for filtering. Used mainly for specifying organisms.

    Returns:
        PubMedArticleResult: List of PubMed articles matching the search.
    """
    result = await PubMedClient().asearch_articles(
        keyword,
        retmax=retmax,
        date_start=date_start,
        date_end=date_end,
        mesh_terms=mesh_terms,
        open_access=open_access,
    )
    return result


@mcp.tool("get_pmc_fulltext")
async def get_fulltext(
    pmid: str,
) -> str:
    """
    Retrieve the full text of a PubMed article as plain text.

    This function downloads the PDF version of an article from PubMed Central
    and extracts the text content.

    Args:
        pmid (str): The PubMed ID of the article.

    Returns:
        str: The full text content of the article.

    Raises:
        RuntimeError: If the article is not available as open access or if there's an error accessing the PDF.
    """
    return await PubMedClient().afetch_fulltext(pmid)


def serve() -> None:
    """
    Start the FastMCP server for PubMed.
    """
    logger.info("Starting PubMed MCP server...")
    mcp.run()


if __name__ == "__main__":
    serve()
