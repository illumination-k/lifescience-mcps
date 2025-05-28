from pydantic import BaseModel, Field


class PubTator3AnnotationInfo(BaseModel):
    identifier: str
    biotype: str
    name: str


class PubTator3Section(BaseModel):
    section_type: str
    annotations: list[PubTator3AnnotationInfo] = Field(default_factory=list)


class PubTator3AnnotationResult(BaseModel):
    """Container for PubTator3 annotations."""

    pmid: str
    pmc_id: str | None = None
    sections: list[PubTator3Section] = Field(default_factory=list)
