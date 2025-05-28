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
from .pdf_parser import extract_text_from_pdf

logger = logging.getLogger(__name__)

SEARCH_URL: Final[str] = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
FETCH_URL: Final[str] = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"


class ErrorMessage(Enum):
    FETCH_ERROR = "Failed to fetch results after multiple attempts."
    PARSE_ERROR = "Failed to parse PubMed XML data."
    PDF_ACCESS_ERROR = "Error accessing PDF for the article."
    NO_PMC_ID = "No PMC ID found for the article."
    NOT_OPEN_ACCESS = "The article is not available as open access."


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

    async def asearch_pmids(
        self,
        keyword: str,
        retmax: int = 30,
        date_start: str | None = None,
        date_end: str | None = None,
        mesh_terms: list[str] | None = None,
    ) -> PubMedSearchResult:
        """
        Asynchronous search for PubMed articles by keyword.

        Args:
            keyword (str): The search term to query PubMed.
            retmax (int): Maximum number of results to return.
            date_start (str, optional): Start date in format YYYY/MM/DD. Used for date range filter.
            date_end (str, optional): End date in format YYYY/MM/DD. Used for date range filter.
            mesh_terms (list[str], optional): List of MeSH terms for filtering. Used mainly for specifying organisms.

        Returns:
            PubMedSearchResult: Object containing PMIDs and search metadata.
        """
        term = keyword

        # Add date filter using [dp] date of publication field if provided
        if date_start and date_end:
            term = f"{term} AND {date_start}:{date_end}[dp]"
        elif date_start:
            term = f"{term} AND {date_start}[dp]"
        elif date_end:
            term = f"{term} AND {date_end}[dp]"

        # Add MeSH term filters if provided
        if mesh_terms and len(mesh_terms) > 0:
            mesh_query = " AND ".join([f'"{term}"[mesh]' for term in mesh_terms])
            term = f"{term} AND ({mesh_query})"

        params = {
            "db": "pubmed",
            "term": term,
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
        self,
        keyword: str,
        retmax: int = 30,
        date_start: str | None = None,
        date_end: str | None = None,
        mesh_terms: list[str] | None = None,
    ) -> PubMedArticleResult:
        """
        Asynchronously search for PubMed articles by keyword.

        Args:
            keyword (str): The search term to query PubMed.
            retmax (int): Maximum number of results to return.
            date_start (str, optional): Start date in format YYYY/MM/DD. Used for date range filter.
            date_end (str, optional): End date in format YYYY/MM/DD. Used for date range filter.
            mesh_terms (list[str], optional): List of MeSH terms for filtering. Used mainly for specifying organisms.

        Returns:
            PubMedArticleResult: Object containing PMIDs and search metadata.
        """
        search_result = await self.asearch_pmids(
            keyword,
            retmax=retmax,
            date_start=date_start,
            date_end=date_end,
            mesh_terms=mesh_terms,
        )
        return await self.afetch_articles(search_result.pmids)

    async def afetch_fulltext(self, pmid: str) -> str:
        """
        Download the full text PDF of a PubMed article.

        Args:
            pmid (str): The PubMed ID of the article.
            save_dir (str): The directory where the PDF will be saved.

        Returns:
            str: The file path of the saved PDF.

        Raises:
            RuntimeError: If there is an error accessing the PDF or if the article is not open access.
        """
        # Fetch the article details to get the PMC ID
        result = await self.afetch_articles(pmid)
        if not result.articles:
            raise RuntimeError(ErrorMessage.NO_PMC_ID.value)

        article = result.articles[0]
        pmc_id = article.pmc_id

        if not pmc_id:
            raise RuntimeError(ErrorMessage.NO_PMC_ID.value)

        # Construct the URL for the PDF download
        pdf_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc_id}/pdf/"

        # Download the PDF
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(pdf_url)

            if response.status_code == 200:
                # Return structured data from the pdf
                text = extract_text_from_pdf(response.content)

                return text
            logger.error(
                "Failed to download PDF, status code: %d", response.status_code
            )
            raise RuntimeError(ErrorMessage.PDF_ACCESS_ERROR.value)
