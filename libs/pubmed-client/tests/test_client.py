import pytest

from pubmed_client.client import PubMedClient


@pytest.mark.asyncio
async def test_asearch_with_real_api():
    """
    Test the asearch method with a real API call.
    This test ensures that the client can successfully connect to PubMed
    and retrieve results for a simple search term.
    """
    # Arrange
    client = PubMedClient()
    keyword = "cancer"  # A common term that should always return results
    retmax = 5  # Limit results for test performance

    # Act
    pmids = await client.asearch(keyword, retmax=retmax)

    # Assert
    assert isinstance(pmids, list), "Return value should be a list"
    assert len(pmids) > 0, "Should return at least one PMID for 'cancer'"
    assert len(pmids) <= retmax, f"Should not return more than {retmax} results"

    # Verify that each returned ID appears to be a valid PMID
    for pmid in pmids:
        assert pmid.isdigit(), f"PMID should be numeric: {pmid}"
