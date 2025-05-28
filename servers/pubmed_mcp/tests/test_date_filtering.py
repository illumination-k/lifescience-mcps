import pytest
from pubmed_mcp.client import PubMedClient
from pubmed_mcp.models import PubMedSearchResult


@pytest.mark.asyncio
async def test_asearch_pmids_with_date_filtering() -> None:
    """
    Test the asearch_pmids method with date filtering parameters.
    This test ensures that the client can successfully connect to PubMed
    and retrieve results filtered by date.
    """
    # Arrange
    client = PubMedClient()
    keyword = "cancer"
    retmax = 5
    date_year = "2022"  # Test with a specific year

    # Act: Search with date filter
    result_with_date = await client.asearch_pmids(
        keyword, retmax=retmax, date_start=date_year
    )

    # Act: Search without date filter for comparison
    result_without_date = await client.asearch_pmids(keyword, retmax=retmax)

    # Assert: Basic validation
    assert isinstance(result_with_date, PubMedSearchResult)
    assert len(result_with_date.pmids) > 0
    assert len(result_with_date.pmids) <= retmax

    # These results should be different due to date filtering
    assert result_with_date.pmids != result_without_date.pmids

    # Test date range filtering
    date_start = "2020/01/01"
    date_end = "2020/12/31"

    # Act: Search with date range
    result_with_date_range = await client.asearch_pmids(
        keyword, retmax=retmax, date_start=date_start, date_end=date_end
    )

    # Assert
    assert isinstance(result_with_date_range, PubMedSearchResult)
    assert len(result_with_date_range.pmids) > 0
    assert len(result_with_date_range.pmids) <= retmax


@pytest.mark.asyncio
async def test_asearch_articles_with_date_filtering() -> None:
    """
    Test the asearch_articles method with date filtering.
    This test ensures that the client can successfully retrieve article details
    filtered by date.
    """
    # Arrange
    client = PubMedClient()
    keyword = "cancer"
    retmax = 3
    date_year = "2022"

    # Act: Search articles with date filter
    result = await client.asearch_articles(keyword, retmax=retmax, date_start=date_year)

    # Assert
    assert len(result.articles) > 0
    assert len(result.articles) <= retmax

    # Add more specific checks if needed
