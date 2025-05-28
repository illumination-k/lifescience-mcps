from mcp.server.fastmcp import FastMCP
from pubmed_client import PubMedClient

mcp = FastMCP("PubMed")



@mcp.tool("search")
async def search(
    keyword: str,
    retmax: int = 30,
) -> list[str]:
    """
    Search PubMed for articles matching the given keyword.

    Args:
        keyword (str): The search term to query PubMed.
        retmax (int): Maximum number of results to return.

    Returns:
        list[str]: List of PubMed IDs (PMIDs) matching the search.
    """
    result = await PubMedClient().asearch_articles(keyword, retmax=retmax)
    return 