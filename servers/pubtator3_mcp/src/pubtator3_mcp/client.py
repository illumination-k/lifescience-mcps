import asyncio
import logging
import re
from typing import Final, Literal

import httpx
from pydantic import ValidationError

from .models import PubTator3AnnotationInfo, PubTator3AnnotationResult, PubTator3Section

logger = logging.getLogger(__name__)

PUBTATOR3_AUTOCOMPLETE_API_ENDPOINT: Final[str] = (
    "https://www.ncbi.nlm.nih.gov/research/pubtator3-api/entity/autocomplete/"
)

PUBTATOR3_ANNOTATION_API_ENDPOINT: Final[str] = (
    "https://www.ncbi.nlm.nih.gov/research/pubtator3-api/publications/export/biocjson"
)

PubTator3Concept = Literal[
    "gene",
    "disease",
    "chemical",
]


def extract_pmid_and_pmc_id(text: str) -> tuple[str, str | None]:
    """
    Extracts the PMID and PMC ID from a given text.

    Args:
        text (str): The input text containing PMID and PMC ID.

    Returns:
        tuple[str, str | None]: A tuple containing the PMID and PMC ID (if available).
    """
    pattern = re.compile(r"(\d+)(?:\|(PMC\d+))?")

    match_ = pattern.match(text)

    if match_:
        pmid = match_.group(1)
        pmc_id = match_.group(2) if match_.group(2) else None
        return pmid, pmc_id
    msg = f"Invalid format for PMID and PMC ID in text: {text}"
    raise ValueError(msg)


class PubTator3Client:
    """
    Client for interacting with the PubTator3 API.
    This client provides methods to autocomplete keywords and retrieve normalized terms.
    """

    def __init__(
        self, timeout: float = 30.0, n_retries: int = 3, n_delay: float = 3.0
    ) -> None:
        self.timeout = timeout
        self.n_retries = n_retries
        self.n_delay = n_delay

    async def _get(self, url: str, params: dict) -> httpx.Response:
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

    async def annotate(self, pmids: list[str]) -> list[PubTator3AnnotationResult]:
        params = {
            "full": True,
            "pmids": ",".join(pmids),
        }

        response = await self._get(PUBTATOR3_ANNOTATION_API_ENDPOINT, params=params)
        results = response.json().get("PubTator3", [])

        ret: list[PubTator3AnnotationResult] = []

        for result in results:
            pmid, pmc_id = extract_pmid_and_pmc_id(result["_id"])
            sections: list[PubTator3Section] = []
            passages = result.get("passages", [])
            for passage in passages:
                passage_infons = passage.get("infons", {})
                section_type = passage.get("infons", {}).get("section_type")
                if section_type is None:
                    section_type = passage_infons.get("type", "unknown")

                annotations: list[PubTator3AnnotationInfo] = []

                for annotation in passage.get("annotations", []):
                    try:
                        annotation_info = PubTator3AnnotationInfo.model_validate(
                            annotation.get("infons")
                        )
                        annotations.append(annotation_info)
                    except ValidationError as e:
                        logger.debug("Validation error for annotation: %s", e)
                        continue

                sections.append(
                    PubTator3Section(
                        section_type=section_type,
                        annotations=annotations,
                    )
                )

            ret.append(
                PubTator3AnnotationResult(pmid=pmid, pmc_id=pmc_id, sections=sections)
            )

        return ret

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

        response = await self._get(PUBTATOR3_AUTOCOMPLETE_API_ENDPOINT, params)
        results = response.json()
        if len(results) == 0:
            return {}
        return results[0]  # Return the first result as a dictionary
