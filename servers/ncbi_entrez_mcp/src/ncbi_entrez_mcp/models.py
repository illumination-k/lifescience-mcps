import dataclasses
from typing import Final, Literal

from pydantic import BaseModel, Field

ENTREZ_ELINK_URL: Final[str] = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi"
ENTREZ_EFETCH_URL: Final[str] = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"


EntrezDatabase = Literal[
    "pubmed",
    "nucleotide",
    "protein",
    "gene",
    "taxonomy",
    "structure",
    "biosample",
    "assembly",
    "variation",
    "sra",
    "bioproject",
    "biocollection",
    "clinvar",
    "snp",
]


class EntrezLink(BaseModel):
    """A link between NCBI database records."""
    
    id: str
    db: str
    linked_ids: list[str] = Field(default_factory=list)


class EntrezLinkResult(BaseModel):
    """Container for multiple Entrez links."""
    
    db_from: str
    db_to: str
    links: list[EntrezLink] = Field(default_factory=list)
