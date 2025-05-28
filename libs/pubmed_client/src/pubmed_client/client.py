import contextlib
import logging
from enum import Enum
from typing import Final

import httpx

from .models import (
    PubMedArticleResult,
    PubMedSearchResult,
)
from .parser import parse_pubmed_xml

logger = logging.getLogger(__name__)

SEARCH_URL: Final[str] = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
FETCH_URL: Final[str] = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"


class ErrorMessage(Enum):
    FETCH_ERROR = "Failed to fetch results after multiple attempts."
    PARSE_ERROR = "Failed to parse PubMed XML data."


class PubMedClient:
    def __init__(
        self,
        timeout: float = 30.0,
        n_retries: int = 3,
    ) -> None:
        self.timeout = timeout
        self.n_retries = n_retries

    async def _get(self, url: str, params: dict) -> httpx.Response:
        """
        Helper method to perform GET requests with retries.

        Args:
            url (str): The URL to request.
            params (dict): Query parameters for the request.

        Returns:
            httpx.Response: The response object from the GET request.
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for attempt in range(self.n_retries):
                try:
                    response = await client.get(url, params=params)
                    response.raise_for_status()
                except httpx.HTTPStatusError:
                    logger.exception("HTTP error on attempt %d", attempt + 1)
                except httpx.RequestError:
                    logger.exception("Request error on attempt %d", attempt + 1)
                else:
                    return response

            raise RuntimeError(ErrorMessage.FETCH_ERROR.value)

    async def asearch_pmids(self, keyword: str, retmax: int = 30) -> PubMedSearchResult:
        """
        Asynchronous search for PubMed articles by keyword.

        Args:
            keyword (str): The search term to query PubMed.
            retmax (int): Maximum number of results to return.

        Returns:
            PubMedSearchResult: Object containing PMIDs and search metadata.
        """
        params = {
            "db": "pubmed",
            "term": keyword,
            "retmode": "json",
            "retmax": str(retmax),
        }

        response = await self._get(SEARCH_URL, params=params)
        data = response.json()

        esearch_result = data.get("esearchresult", {})
        pmids = esearch_result.get("idlist", [])
        total_results = None
        query_translation = None

        # Extract additional metadata if available
        if "count" in esearch_result:
            with contextlib.suppress(ValueError, TypeError):
                total_results = int(esearch_result["count"])

        if "querytranslation" in esearch_result:
            query_translation = esearch_result["querytranslation"]

        return PubMedSearchResult(
            pmids=pmids,
            total_results=total_results,
            query_translation=query_translation,
        )

    async def _afetch_articles_xml(self, pmids: str | list[str]) -> str:
        """
        Asynchronously fetch article details using PubMed IDs.

        Args:
            pmids (Union[str, List[str]]): A single PMID or list of PMIDs.

        Returns:
            str: XML data as a string.
        """
        # Convert single PMID to list if necessary
        if isinstance(pmids, str):
            pmids = [pmids]

        # Join multiple PMIDs with comma for the API request
        id_str = ",".join(pmids)

        params = {
            "db": "pubmed",
            "id": id_str,
            "retmode": "xml",
        }

        resp = await self._get(FETCH_URL, params=params)
        return resp.text

    async def afetch_articles(self, pmids: str | list[str]) -> PubMedArticleResult:
        """
        Asynchronously fetch article details using PubMed IDs.

        Args:
            pmids (Union[str, List[str]]): A single PMID or list of PMIDs.
            retmode (str): The format of the returned data. Default is "xml".
                           Other options include "text" for plain text.

        Returns:
            PubMedArticleResult: Article details in the specified format wrapped in a Pydantic model.
        """
        # Convert single PMID to list if necessary
        if isinstance(pmids, str):
            pmids = [pmids]

        return parse_pubmed_xml(await self._afetch_articles_xml(pmids))

    async def asearch_articles(
        self, keyword: str, retmax: int = 30
    ) -> PubMedArticleResult:
        """
        Asynchronously search for PubMed articles by keyword.

        Args:
            keyword (str): The search term to query PubMed.
            retmax (int): Maximum number of results to return.

        Returns:
            PubMedSearchResult: Object containing PMIDs and search metadata.
        """
        search_result = await self.asearch_pmids(keyword, retmax)
        return await self.afetch_articles(search_result.pmids)
