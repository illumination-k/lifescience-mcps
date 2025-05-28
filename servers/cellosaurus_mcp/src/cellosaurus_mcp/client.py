import asyncio
import logging
from typing import Any, Final

import httpx
from pydantic import ValidationError

from .models import CellosaurusCellLine, CellosaurusSearchResult

logger = logging.getLogger(__name__)

CELLOSAURUS_API_ENDPOINT: Final[str] = "https://api.cellosaurus.org"
CELLOSAURUS_SEARCH_ENDPOINT: Final[str] = f"{CELLOSAURUS_API_ENDPOINT}/search/cell-line"
CELLOSAURUS_CELL_LINE_ENDPOINT: Final[str] = f"{CELLOSAURUS_API_ENDPOINT}/cell-line"


class CellosaurusClient:
    """
    Client for interacting with the Cellosaurus API.
    This client provides methods to search for cell lines and retrieve detailed information.
    """

    def __init__(
        self, timeout: float = 30.0, n_retries: int = 3, n_delay: float = 3.0
    ) -> None:
        """
        Initialize the Cellosaurus API client.

        Args:
            timeout: Request timeout in seconds.
            n_retries: Number of times to retry failed requests.
            n_delay: Delay between retries in seconds.
        """
        self.timeout = timeout
        self.n_retries = n_retries
        self.n_delay = n_delay

    async def _get(self, url: str, params: dict[str, Any]) -> httpx.Response:
        """
        Make a GET request to the Cellosaurus API with retry logic.

        Args:
            url: The API endpoint URL.
            params: Query parameters to include in the request.

        Returns:
            The API response.

        Raises:
            httpx.HTTPError: If all retry attempts fail.
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for attempt in range(self.n_retries):
                try:
                    response = await client.get(url, params=params)
                    response.raise_for_status()
                    return response
                except httpx.HTTPError as e:
                    logger.error(f"Error fetching {url}: {e}")
                    if attempt < self.n_retries - 1:
                        await asyncio.sleep(self.n_delay)
            raise httpx.HTTPError(
                f"Failed to fetch {url} after {self.n_retries} attempts"
            )

    async def search_cell_lines(
        self,
        query: str,
        fields: list[str] | None = None,
        page: int = 1,
        page_size: int = 10,
    ) -> CellosaurusSearchResult:
        """
        Search for cell lines in Cellosaurus based on query parameters.

        Args:
            query: The search query string using Cellosaurus search syntax.
                  Examples:
                  - "ox:sapiens" (human cell lines)
                  - "derived-from-site:liver" (cell lines from liver)
                  - "di:Hepatoblastoma" (cell lines from hepatoblastoma patients)
            fields: List of specific fields to return. If None, all fields are returned.
            page: Page number for pagination.
            page_size: Number of results per page.

        Returns:
            CellosaurusSearchResult containing search results.
        """
        params: dict[str, Any] = {
            "q": query,
            "format": "json",
            "page": page,
            "size": page_size,
        }

        if fields:
            params["fields"] = ",".join(fields)

        response = await self._get(CELLOSAURUS_SEARCH_ENDPOINT, params)
        response_data = response.json()

        # Process the response data
        result = CellosaurusSearchResult(
            total_count=response_data.get("total_count", 0), cell_lines=[]
        )

        for cell_line_data in response_data.get("cell_lines", []):
            try:
                cell_line = CellosaurusCellLine.model_validate(cell_line_data)
                result.cell_lines.append(cell_line)
            except ValidationError as e:
                logger.debug(f"Validation error for cell line: {e}")
                continue

        return result
