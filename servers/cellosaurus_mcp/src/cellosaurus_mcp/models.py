from typing import Any

from pydantic import BaseModel, Field


class CellosaurusStrProfile(BaseModel):
    """STR (Short Tandem Repeat) profile information for a cell line."""

    marker: str
    allele: list[str]
    source: str | None = None


class CellosaurusDisease(BaseModel):
    """Disease information associated with a cell line."""

    name: str
    identifier: str  # NCI Thesaurus or ORDO code


class CellosaurusSequenceVariation(BaseModel):
    """Sequence variation information for a cell line."""

    gene: str
    description: str


class CellosaurusPublication(BaseModel):
    """Publication reference for a cell line."""

    pubmed_id: str | None = None
    title: str
    authors: str | None = None
    reference: str


class CellosaurusCellLine(BaseModel):
    """Detailed information about a Cellosaurus cell line."""

    accession: str
    name: str
    synonyms: list[str] = Field(default_factory=list)
    category: str
    species: str
    sex: str | None = None
    age: str | None = None
    derived_from_site: str | None = None
    str_profile: list[CellosaurusStrProfile] = Field(default_factory=list)
    diseases: list[CellosaurusDisease] = Field(default_factory=list)
    sequence_variations: list[CellosaurusSequenceVariation] = Field(
        default_factory=list
    )
    publications: list[CellosaurusPublication] = Field(default_factory=list)
    comments: dict[str, Any] = Field(default_factory=dict)
    cross_references: dict[str, list[str]] = Field(default_factory=dict)


class CellosaurusSearchResult(BaseModel):
    """Container for Cellosaurus search results."""

    total_count: int
    cell_lines: list[CellosaurusCellLine] = Field(default_factory=list)
