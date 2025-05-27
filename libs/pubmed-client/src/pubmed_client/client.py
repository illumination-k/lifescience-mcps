import httpx
import logging

from typing import Final

logger = logging.getLogger(__name__)

SEARCH_URL: Final[str] = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"


class PubMedClient:
    def __init__(
        self,
        timeout: float = 30.0,
        n_retries: int = 3,
    ) -> None:
        self.timeout = timeout
        self.n_retries = n_retries

    async def asearch(self, keyword: str, retmax: int = 30) -> list[str]:
        """
        Asynchronous search for PubMed articles by keyword.

        Args:
            keyword (str): The search term to query PubMed.
            retmax (int): Maximum number of results to return.

        Returns:
            list[str]: List of PubMed IDs (PMIDs) matching the search term.
        """
        params = {
            "db": "pubmed",
            "term": keyword,
            "retmode": "json",
            "retmax": str(retmax),
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for attempt in range(self.n_retries):
                try:
                    response = await client.get(SEARCH_URL, params=params)
                    response.raise_for_status()
                    data = response.json()
                    return data["esearchresult"].get("idlist", [])
                except httpx.HTTPStatusError as e:
                    logger.error(f"HTTP error on attempt {attempt + 1}: {e}")
                except httpx.RequestError as e:
                    logger.error(f"Request error on attempt {attempt + 1}: {e}")

            raise RuntimeError("Failed to fetch results after multiple attempts.")
