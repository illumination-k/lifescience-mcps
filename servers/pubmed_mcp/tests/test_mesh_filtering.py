import pytest
from pubmed_mcp.client import PubMedClient
from pubmed_mcp.models import PubMedSearchResult


@pytest.mark.asyncio
async def test_asearch_pmids_with_mesh_filtering() -> None:
    """
    Test the asearch_pmids method with MeSH term filtering.
    This test ensures that the client can successfully connect to PubMed
    and retrieve results filtered by MeSH terms.
    """
    # Arrange
    client = PubMedClient()
    keyword = "cancer"
    retmax = 5
    mesh_terms = ["Humans"]  # Filter for human studies

    # Act: Search with MeSH filter
    result_with_mesh = await client.asearch_pmids(
        keyword, retmax=retmax, mesh_terms=mesh_terms
    )

    # Act: Search without MeSH filter for comparison
    result_without_mesh = await client.asearch_pmids(keyword, retmax=retmax)

    # Assert: Basic validation
    assert isinstance(result_with_mesh, PubMedSearchResult)
    assert len(result_with_mesh.pmids) > 0
    assert len(result_with_mesh.pmids) <= retmax

    # These results should be different due to MeSH filtering
    assert result_with_mesh.pmids != result_without_mesh.pmids

    # Test with multiple MeSH terms
    multiple_mesh_terms = ["Humans", "Female"]

    # Act: Search with multiple MeSH terms
    result_with_multiple_mesh = await client.asearch_pmids(
        keyword, retmax=retmax, mesh_terms=multiple_mesh_terms
    )

    # Assert
    assert isinstance(result_with_multiple_mesh, PubMedSearchResult)
    assert len(result_with_multiple_mesh.pmids) > 0
    assert len(result_with_multiple_mesh.pmids) <= retmax


@pytest.mark.asyncio
async def test_asearch_articles_with_mesh_filtering() -> None:
    """
    Test the asearch_articles method with MeSH filtering.
    This test ensures that the client can successfully retrieve article details
    filtered by MeSH terms.
    """
    # Arrange
    client = PubMedClient()
    keyword = "cancer"
    retmax = 3
    mesh_terms = ["Mice"]  # Filter for mice studies

    # Act: Search articles with MeSH filter
    result = await client.asearch_articles(
        keyword, retmax=retmax, mesh_terms=mesh_terms
    )

    # Assert
    assert len(result.articles) > 0
    assert len(result.articles) <= retmax

    # Test combined filtering (MeSH terms + date)
    date_year = "2022"
    combined_result = await client.asearch_articles(
        keyword, retmax=retmax, mesh_terms=mesh_terms, date_start=date_year
    )

    # Assert combined filtering
    assert len(combined_result.articles) > 0
    assert len(combined_result.articles) <= retmax
