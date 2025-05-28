import pytest
from pubmed_client.client import PubMedClient
from pubmed_client.models import (
    PubMedArticle,
    PubMedArticleResult,
    PubMedSearchResult,
)


@pytest.mark.asyncio
async def test_asearch_pmids_with_real_api() -> None:
    """
    Test the asearch_pmids method with a real API call.
    This test ensures that the client can successfully connect to PubMed
    and retrieve results for a simple search term.
    """
    # Arrange
    client = PubMedClient()
    keyword = "cancer"  # A common term that should always return results
    retmax = 5  # Limit results for test performance

    # Act
    result = await client.asearch_pmids(keyword, retmax=retmax)

    # Assert
    assert isinstance(result, PubMedSearchResult), (
        "Return value should be a PubMedSearchResult"
    )
    assert len(result.pmids) > 0, "Should return at least one PMID for 'cancer'"
    assert len(result.pmids) <= retmax, f"Should not return more than {retmax} results"

    # Check that total_results is present
    assert result.total_results is not None, "Total results should be set"
    assert result.total_results > 0, "Total results should be greater than zero"

    # Verify that each returned ID appears to be a valid PMID
    for pmid in result.pmids:
        assert pmid.isdigit(), f"PMID should be numeric: {pmid}"


@pytest.mark.asyncio
async def test_afetch_articles_with_real_api() -> None:
    """
    Test the afetch_articles method with a real API call.
    This test ensures that the client can successfully retrieve article details
    using known PMIDs.
    """
    # Arrange
    client = PubMedClient()
    # Use PMID for a well-known article
    pmid = "33831944"  # Sample PubMed ID

    # Act
    result = await client.afetch_articles(pmid)

    # Assert
    assert isinstance(result, PubMedArticleResult), (
        "Return value should be a PubMedArticleResult"
    )
    assert len(result.articles) > 0, "Should return at least one article"

    # Check that the article contains the requested PMID
    article = result.articles[0]
    assert article.pmid == pmid, "Article PMID should match the requested PMID"
    assert article.title is not None, "Article should have a title"
    assert article.journal is not None, "Article should have journal information"

    # Test with multiple PMIDs
    pmids = [pmid, "34161778"]  # Two sample PubMed IDs
    result_multi = await client.afetch_articles(pmids)

    # Assert for multiple PMIDs
    assert isinstance(result_multi, PubMedArticleResult), (
        "Return value should be a PubMedArticleResult"
    )
    assert len(result_multi.articles) > 0, "Should return at least one article"

    # Check that the articles contain the requested PMIDs
    found_pmids = [a.pmid for a in result_multi.articles]
    for p in pmids:
        assert p in found_pmids, f"Results should include PMID {p}"


@pytest.mark.asyncio
async def test_afetch_articles_xml() -> None:
    """
    Test the _afetch_articles_xml internal method with real data.

    Note: This test directly accesses a private method for testing purposes.
    The SLF001 rule is ignored here as we explicitly want to test this internal method.
    """
    # Arrange
    client = PubMedClient()
    pmid = "33831944"  # Sample PubMed ID

    # Act
    xml_data = await client._afetch_articles_xml(pmid)  # noqa: SLF001

    # Assert
    assert isinstance(xml_data, str), "Return value should be a string of XML data"
    assert len(xml_data) > 0, "XML data should not be empty"
    assert "PubmedArticle" in xml_data, "XML data should contain PubmedArticle element"
    assert pmid in xml_data, "XML data should contain the requested PMID"

    # Test with multiple PMIDs
    pmids = [pmid, "34161778"]  # Two sample PubMed IDs
    xml_data_multi = await client._afetch_articles_xml(pmids)  # noqa: SLF001

    # Assert for multiple PMIDs
    assert isinstance(xml_data_multi, str), (
        "Return value should be a string of XML data"
    )
    assert len(xml_data_multi) > 0, "XML data should not be empty"
    assert all(p in xml_data_multi for p in pmids), (
        "XML should contain all requested PMIDs"
    )


@pytest.mark.asyncio
async def test_asearch_articles() -> None:
    """
    Test the asearch_articles method with real data.
    This combines searching and fetching articles in one operation.
    """
    # Arrange
    client = PubMedClient()
    keyword = "cancer"  # A common term that should always return results
    retmax = 3  # Limit results for test performance

    # Act
    result = await client.asearch_articles(keyword, retmax=retmax)

    # Assert
    assert isinstance(result, PubMedArticleResult), (
        "Result should be a PubMedArticleResult"
    )
    assert len(result.articles) > 0, "Should have at least one article"
    assert len(result.articles) <= retmax, (
        f"Should not return more than {retmax} articles"
    )
    assert all(isinstance(a, PubMedArticle) for a in result.articles), (
        "All items should be PubMedArticle objects"
    )

    # Verify that articles have essential fields
    for article in result.articles:
        assert article.pmid is not None, "Each article should have a PMID"
        assert article.pmid.isdigit(), f"PMID should be numeric: {article.pmid}"
