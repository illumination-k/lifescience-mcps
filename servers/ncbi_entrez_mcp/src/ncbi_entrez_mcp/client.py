# filepath: /Users/illumination27/ghq/github.com/illumination-k/lifescience-mcps/servers/ncbi_entrez_mcp/src/ncbi_entrez_mcp/client.py
import contextlib
import logging
import xml.etree.ElementTree as ET
from typing import Final, Literal

import httpx
from pydantic import ValidationError

from .models import ENTREZ_ELINK_URL, ENTREZ_EFETCH_URL, EntrezDatabase, EntrezLink, EntrezLinkResult

logger = logging.getLogger(__name__)


class ErrorMessage:
    """Error messages for the NCBI Entrez eLink client."""
    
    FETCH_ERROR: Final[str] = "Failed to fetch results after multiple attempts."
    PARSE_ERROR: Final[str] = "Failed to parse Entrez eLink XML data."
    NO_LINKS_FOUND: Final[str] = "No links found between the specified databases."


class EntrezElinkClient:
    """
    Client for the NCBI Entrez eLink API.
    
    This client provides methods to discover links between NCBI database records,
    such as finding related PubMed articles, or retrieving gene information
    from an article ID.
    """
    
    def __init__(
        self,
        timeout: float = 30.0,
        n_retries: int = 3,
        api_key: str | None = None,
        email: str | None = None,
        tool: str = "python-ncbi-entrez-mcp",
    ) -> None:
        """
        Initialize the EntrezElinkClient.
        
        Args:
            timeout (float): HTTP request timeout in seconds.
            n_retries (int): Number of retry attempts for failed requests.
            api_key (str | None): NCBI API key for higher rate limits.
            email (str | None): Email address for NCBI to contact if there are issues.
            tool (str): Name of the tool/application making the request.
        """
        self.timeout = timeout
        self.n_retries = n_retries
        self.api_key = api_key
        self.email = email
        self.tool = tool
    
    async def _get(
        self,
        url: str,
        params: dict | None = None,
    ) -> httpx.Response:
        """
        Helper method to perform GET requests with retries.
        
        Args:
            url (str): The URL to request.
            params (dict | None): Query parameters for the request.
            
        Returns:
            httpx.Response: The response object from the GET request.
            
        Raises:
            RuntimeError: If all request attempts fail.
        """
        # Add authentication parameters if provided
        if params is None:
            params = {}
        
        if self.email:
            params["email"] = self.email
        if self.api_key:
            params["api_key"] = self.api_key
        if self.tool:
            params["tool"] = self.tool
        
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
            
            raise RuntimeError(ErrorMessage.FETCH_ERROR)
    
    def _parse_elink_response(self, xml_data: str, db_from: str, db_to: str) -> EntrezLinkResult:
        """
        Parse XML response from eLink API into structured data.
        
        Args:
            xml_data (str): The XML response from the eLink API.
            db_from (str): The source database.
            db_to (str): The target database.
            
        Returns:
            EntrezLinkResult: Structured data containing the links between records.
            
        Raises:
            ValueError: If the XML cannot be parsed or has an unexpected structure.
        """
        try:
            result = EntrezLinkResult(db_from=db_from, db_to=db_to)
            
            root = ET.fromstring(xml_data)
            link_set_db_elements = root.findall(".//LinkSetDb")
            
            if not link_set_db_elements:
                logger.warning("No LinkSetDb elements found in the response")
                return result
            
            for link_set_db in link_set_db_elements:
                # Check if this LinkSetDb is for the target database
                db_to_element = link_set_db.find("DbTo")
                if db_to_element is None or db_to_element.text != db_to:
                    continue
                
                # Process each source ID
                id_elements = root.findall(".//IdList/Id")
                for id_elem in id_elements:
                    if id_elem is not None and id_elem.text:
                        source_id = id_elem.text
                        link = EntrezLink(id=source_id, db=db_from)
                        
                        # Find all target IDs linked to this source ID
                        link_elements = link_set_db.findall(".//Link")
                        for link_elem in link_elements:
                            target_id_elem = link_elem.find("Id")
                            if target_id_elem is not None and target_id_elem.text:
                                link.linked_ids.append(target_id_elem.text)
                        
                        if link.linked_ids:
                            result.links.append(link)
            
            return result
        
        except ET.ParseError as e:
            logger.exception("Failed to parse eLink XML response: %s", e)
            raise ValueError(ErrorMessage.PARSE_ERROR) from e
        except ValidationError as e:
            logger.exception("Failed to validate parsed data: %s", e)
            raise ValueError(ErrorMessage.PARSE_ERROR) from e
    
    async def aget_links(
        self,
        ids: list[str],
        db_from: EntrezDatabase,
        db_to: EntrezDatabase,
    ) -> EntrezLinkResult:
        """
        Asynchronously get links between records in NCBI databases.
        
        Args:
            ids (list[str]): List of IDs from the source database.
            db_from (EntrezDatabase): Source database.
            db_to (EntrezDatabase): Target database.
            
        Returns:
            EntrezLinkResult: Container with links between database records.
            
        Raises:
            ValueError: If there's an error parsing the response.
            RuntimeError: If the request fails after retries.
        """
        params = {
            "dbfrom": db_from,
            "db": db_to,
            "id": ",".join(ids),
            "retmode": "xml",
        }
        
        response = await self._get(ENTREZ_ELINK_URL, params=params)
        
        if response.status_code == 200:
            return self._parse_elink_response(response.text, db_from, db_to)
        else:
            logger.error("Failed to fetch links: HTTP %d", response.status_code)
            raise RuntimeError(ErrorMessage.FETCH_ERROR)
    
    async def aefetch(
        self,
        ids: list[str],
        db: EntrezDatabase,
        retmode: str = "xml",
        rettype: str | None = None,
    ) -> str:
        """
        Asynchronously fetch raw data from NCBI databases using EFetch.
        
        Args:
            ids (list[str]): List of IDs to retrieve data for.
            db (EntrezDatabase): The database to fetch from.
            retmode (str): The format of the response, defaults to xml.
            rettype (str | None): Additional parameter to specify the type of data to retrieve.
            
        Returns:
            str: Raw data from the EFetch API in the specified format.
            
        Raises:
            RuntimeError: If the request fails after retries.
        """
        params = {
            "db": db,
            "id": ",".join(ids),
            "retmode": retmode,
        }
        
        if rettype:
            params["rettype"] = rettype
        
        response = await self._get(ENTREZ_EFETCH_URL, params=params)
        
        if response.status_code == 200:
            return response.text
        else:
            logger.error("Failed to fetch data: HTTP %d", response.status_code)
            raise RuntimeError(ErrorMessage.FETCH_ERROR)
