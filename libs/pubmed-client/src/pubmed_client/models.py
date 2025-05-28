from pydantic import BaseModel, Field


class Author(BaseModel):
    """Author of a PubMed article."""

    last_name: str | None = None
    fore_name: str | None = None
    initials: str | None = None

    @property
    def full_name(self) -> str:
        """Returns the full name of the author if available."""
        if self.fore_name and self.last_name:
            return f"{self.fore_name} {self.last_name}"
        if self.last_name:
            return self.last_name
        return ""


class Journal(BaseModel):
    """Journal information for a PubMed article."""

    title: str | None = None
    iso_abbreviation: str | None = None
    pub_date: str | None = None


class PubMedArticle(BaseModel):
    """Representation of a PubMed article."""

    pmid: str
    title: str | None = None
    abstract: str | None = None
    journal: Journal | None = None
    authors: list[Author] = Field(default_factory=list)


class PubMedSearchResult(BaseModel):
    """Results from a PubMed search query."""

    pmids: list[str] = Field(default_factory=list)
    total_results: int | None = None
    query_translation: str | None = None


class PubMedArticleResult(BaseModel):
    """Container for multiple PubMed articles."""

    articles: list[PubMedArticle] = Field(default_factory=list)
