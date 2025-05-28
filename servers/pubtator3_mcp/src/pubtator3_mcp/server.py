import logging
from typing import Final, Literal

from mcp.server.fastmcp import FastMCP

from .client import PubTator3Client
from .models import PubTator3AnnotationResult

logger = logging.getLogger(__name__)

PUBTATOR3_API_ENDPOINT: Final[str] = (
    "https://www.ncbi.nlm.nih.gov/research/pubtator3-api/entity/autocomplete/"
)

PubTator3Concept = Literal[
    "gene",
    "disease",
    "chemical",
]

mcp = FastMCP("PubTator3-MCP")


@mcp.tool("pubtator3_annotate")
async def annotate(
    pmids: list[str],
) -> list[PubTator3AnnotationResult]:
    """
    Annotate paper in pubmed using the PubTator3 API.
    This function can extract terms related to genes, diseases, chemicals, or species from text and return the normalized terms.

    Args:
        pmids (list[str]): List of PubMed IDs to annotate.
    """
    client = PubTator3Client()
    return await client.annotate(pmids=pmids)


@mcp.tool("pubtator3_autocomplete")
async def autocomplete(
    keyword: str,
    concept: PubTator3Concept | None = None,
) -> dict:
    """
    Autocomplete keywords using the PubTator3 API.
    This function can extract terms related to genes, diseases, chemicals, or species from keywords and return the normalized terms.

    Args:
        keyword (str): The keyword to autocomplete.
        concept (PubTator3Concept, optional): The concept type to filter results by.
            Can be one of "gene", "disease", "chemical", or "species".
    """
    client = PubTator3Client()
    return await client.autocomplete(keyword, concept)


def serve() -> None:
    """
    Start the FastMCP server for PubTator3.
    """
    logger.info("Starting PubTator3-MCP server...")
    mcp.run()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    serve()
