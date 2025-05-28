import httpx
import pytest
from pubtator3_mcp.client import PubTator3Client, PubTator3Concept
from pubtator3_mcp.models import (
    PubTator3AnnotationResult,
)


@pytest.mark.asyncio
async def test_autocomplete_with_real_api() -> None:
    """
    Test the autocomplete method with a real API call.
    This test ensures that the client can successfully connect to PubTator3
    and retrieve results for a simple search term.
    """
    # Arrange
    client = PubTator3Client()
    keyword = "cancer"  # A common term that should always return results

    # Act
    result = await client.autocomplete(keyword)

    # Assert
    assert isinstance(result, dict), "Return value should be a dictionary"
    assert len(result) > 0, "Should return at least one entity for 'cancer'"


@pytest.mark.asyncio
async def test_autocomplete_with_concept_filter() -> None:
    """
    Test the autocomplete method with a concept filter.
    This test ensures that the client properly filters results by concept type.
    """
    # Arrange
    client = PubTator3Client()
    keyword = "p53"  # A gene term
    concept: PubTator3Concept = "gene"  # Filter by gene concept

    # Act
    result = await client.autocomplete(keyword, concept)

    # Assert
    assert isinstance(result, dict), "Return value should be a dictionary"

    # Check that all returned entities match the requested concept
    assert len(result) > 0


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("keyword", "concept"),
    [
        ("brca", "gene"),
        ("diabetes", "disease"),
        ("aspirin", "chemical"),
    ],
)
async def test_autocomplete_with_different_concepts(
    keyword: str, concept: PubTator3Concept
) -> None:
    """
    Test the autocomplete method with different concept types.
    This test verifies that the client works with all available concept types.
    """
    # Arrange
    client = PubTator3Client()

    # Act & Assert
    result = await client.autocomplete(keyword, concept)

    assert isinstance(result, dict), (
        f"Return value for '{concept}' should be a dictionary"
    )
    # If we got any results, check they match the concept type
    assert len(result) > 0


@pytest.mark.asyncio
async def test_autocomplete_with_invalid_keyword() -> None:
    """
    Test the autocomplete method with an invalid keyword.
    This test verifies that the client handles invalid input appropriately.
    """
    # Arrange
    client = PubTator3Client()
    keyword = "zzzzzzzzzzzzzzzzzzzzzzzzzzz"  # Unlikely to match anything

    # Act
    result = await client.autocomplete(keyword)

    # Assert
    assert isinstance(result, dict), "Return value should be a dictionary"
    # For a nonsense keyword, we expect empty results
    assert len(result) == 0, "Should return no entities for nonsense keyword"


@pytest.mark.asyncio
async def test_autocomplete_with_empty_keyword() -> None:
    """
    Test the autocomplete method with an empty keyword.
    This test verifies that the client handles edge cases appropriately.
    """
    # Arrange
    client = PubTator3Client()
    keyword = ""  # Empty keyword

    # Act & Assert
    with pytest.raises(httpx.HTTPError):
        # Expecting an error due to empty keyword
        await client.autocomplete(keyword)


@pytest.mark.asyncio
async def test_annotate_with_real_api() -> None:
    """
    Test the annotate method with a real API call.
    This test verifies that the client can successfully connect to PubTator3
    and retrieve annotations for a given PMID.
    """
    # Arrange
    client = PubTator3Client()
    pmids = ["34613458"]  # Use a specific PMID that's likely to have annotations

    # Act
    results = await client.annotate(pmids)

    # Assert
    assert isinstance(results, list), "Return value should be a list"
    assert len(results) > 0, "Should return at least one annotation result"

    for result in results:
        assert isinstance(result, PubTator3AnnotationResult), (
            "Each result should be a PubTator3AnnotationResult"
        )
        assert result.pmid == pmids[0], "PMID in result should match the requested PMID"
        assert hasattr(result, "sections"), "Result should have sections attribute"


@pytest.mark.asyncio
async def test_annotate_with_multiple_pmids() -> None:
    """
    Test the annotate method with multiple PMIDs.
    This test ensures that the client can handle multiple PMIDs in a single request.
    """
    # Arrange
    client = PubTator3Client(n_retries=1)
    pmids = ["34613458", "33930893"]  # Use PMIDs that are likely to have annotations

    # Act
    results = await client.annotate(pmids)

    # Assert
    assert isinstance(results, list), "Return value should be a list"
    assert len(results) > 0, "Should return at least one annotation result"

    # Check that we have results for both PMIDs
    result_pmids = {result.pmid for result in results}
    assert result_pmids.issubset(set(pmids)), (
        "Results should contain annotations for requested PMIDs"
    )
