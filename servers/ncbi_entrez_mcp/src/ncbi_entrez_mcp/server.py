import logging
from typing import Literal

from mcp.server.fastmcp import FastMCP

from ncbi_entrez_mcp import EntrezElinkClient, EntrezDatabase, EntrezLinkResult

logger = logging.getLogger(__name__)
mcp = FastMCP("NCBI-Entrez-MCP")


@mcp.tool("get_links")
async def get_links(
    ids: list[str],
    db_from: EntrezDatabase,
    db_to: EntrezDatabase,
    api_key: str | None = None,
    email: str | None = None,
) -> EntrezLinkResult:
    """
    Get links between NCBI database records.

    This function finds relationships between records in different NCBI databases,
    such as linking PubMed articles to genes or proteins.

    Args:
        ids (list[str]): List of IDs from the source database.
        db_from (EntrezDatabase): Source database.
        db_to (EntrezDatabase): Target database.
        api_key (str, optional): NCBI API key for higher rate limits.
        email (str, optional): Email address for NCBI to contact if there are issues.

    Returns:
        EntrezLinkResult: Container with links between database records.
    """
    client = EntrezElinkClient(api_key=api_key, email=email)
    return await client.aget_links(ids=ids, db_from=db_from, db_to=db_to)


@mcp.tool("fetch_data")
async def fetch_data(
    ids: list[str],
    db: EntrezDatabase,
    retmode: Literal["xml", "text", "json"] = "xml",
    rettype: str | None = None,
    api_key: str | None = None,
    email: str | None = None,
) -> str:
    """
    Fetch raw data from NCBI databases using EFetch.

    This function retrieves data directly from NCBI databases in the requested format.

    Args:
        ids (list[str]): List of IDs to retrieve data for.
        db (EntrezDatabase): The database to fetch from.
        retmode (str): The format of the response (xml, text, or json).
        rettype (str, optional): Additional parameter to specify the type of data to retrieve.
        api_key (str, optional): NCBI API key for higher rate limits.
        email (str, optional): Email address for NCBI to contact if there are issues.

    Returns:
        str: Raw data from the EFetch API in the specified format.
    """
    client = EntrezElinkClient(api_key=api_key, email=email)
    return await client.aefetch(ids=ids, db=db, retmode=retmode, rettype=rettype)


def serve() -> None:
    """
    Start the FastMCP server for NCBI Entrez.
    """
    logger.info("Starting NCBI-Entrez-MCP server...")
    mcp.run()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    serve()
