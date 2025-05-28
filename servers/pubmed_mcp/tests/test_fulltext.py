import pytest
from pubmed_mcp.client import ErrorMessage, PubMedClient


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
    assert len(full_text) > 100, "Extracted text should be substantial (>100 chars)"

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


@pytest.mark.asyncio
async def test_afetch_fulltext_no_pmc_id() -> None:
    """
    Test the afetch_fulltext method with a PMID that doesn't have a PMC ID.
    This test verifies appropriate error handling when article doesn't have PMC access.
    """
    # Arrange
    client = PubMedClient()
    # Using a PMID known not to have a PMC ID (not open access)
    # The exact PMID doesn't matter as we'll mock the result
    pmid = "12345678"  # Sample PMID without PMC ID

    # We'll patch the afetch_articles method to return an article without a PMC ID
    original_afetch_articles = client.afetch_articles

    async def mock_afetch_articles(*args, **kwargs):
        from pubmed_mcp.models import Journal, PubMedArticle, PubMedArticleResult

        # Create a result with an article that has no PMC ID
        article = PubMedArticle(
            pmid=pmid,
            pmc_id=None,  # No PMC ID
            title="Test Article",
            journal=Journal(title="Test Journal"),
        )
        return PubMedArticleResult(articles=[article])

    # Apply the mock
    client.afetch_articles = mock_afetch_articles

    # Act & Assert
    with pytest.raises(RuntimeError) as excinfo:
        await client.afetch_fulltext(pmid)

    # Check that the correct error message is raised
    assert str(excinfo.value) == ErrorMessage.NO_PMC_ID.value

    # Restore the original method
    client.afetch_articles = original_afetch_articles
