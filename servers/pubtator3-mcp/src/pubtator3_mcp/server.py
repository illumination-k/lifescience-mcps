import logging
from typing import Final, Literal

import httpx
from mcp.server.fastmcp import FastMCP

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


class PubTator3Client:
    """
    Client for interacting with the PubTator3 API.
    This client provides methods to autocomplete keywords and retrieve normalized terms.
    """

    def __init__(self, timeout: float = 30.0) -> None:
        self.timeout = timeout

    async def autocomplete(
        self, keyword: str, concept: PubTator3Concept | None = None
    ) -> dict:
        """
        Autocomplete keywords using the PubTator3 API.

        Args:
            keyword (str): The keyword to autocomplete.
            concept (PubTator3Concept, optional): The concept type to filter results by.
                Can be one of "gene", "disease", "chemical", or "species".

        Returns:
            dict: The response from the PubTator3 API containing normalized terms.
        """
        params = {"query": keyword, "limit": 1}

        if concept:
            params["concept"] = concept

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(PUBTATOR3_API_ENDPOINT, params=params)
            response.raise_for_status()
            results = response.json()
            if len(results) == 0:
                return {}
            return results[0]  # Return the first result as a dictionary


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
