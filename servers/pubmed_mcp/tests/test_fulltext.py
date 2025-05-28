import pytest
from pubmed_mcp.client import PubMedClient


@pytest.mark.asyncio
async def test_afetch_fulltext_with_real_api() -> None:
    """
    Test the afetch_fulltext method with a real API call using a known open access PMID.
    This test confirms that the method can successfully retrieve and extract
    the full text content from a PMC article.
    """
    # Arrange
    client = PubMedClient()
    pmid = "40062421"  # PMID for an open access article

    # Act
    full_text = await client.afetch_fulltext(pmid)

    # Assert
    assert isinstance(full_text, str), "Return value should be a string"

    # Define minimum text length for a substantial article
    min_text_length = 100
    assert len(full_text) > min_text_length, (
        f"Extracted text should be substantial (>{min_text_length} chars)"
    )

    # Check for common scientific article sections
    # These checks are not case-sensitive and allow for variations in formatting
    common_terms = [
        "abstract",
        "introduction",
        "methods",
        "results",
        "discussion",
        "conclusion",
        "reference",
    ]
    text_lower = full_text.lower()

    # At least some of these terms should appear in a scientific paper
    assert any(term in text_lower for term in common_terms), (
        "Full text should contain common scientific article sections"
    )
