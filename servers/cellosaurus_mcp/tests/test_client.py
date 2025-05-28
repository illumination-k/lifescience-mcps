import httpx
import pytest
from cellosaurus_mcp.client import CellosaurusClient
from cellosaurus_mcp.models import CellosaurusCellLine, CellosaurusSearchResult


@pytest.mark.asyncio
async def test_search_cell_lines_with_real_api() -> None:
    """
    Test the search_cell_lines method with a real API call.
    This test ensures that the client can successfully connect to Cellosaurus
    and retrieve search results for a simple query.
    """
    # Arrange
    client = CellosaurusClient()
    # Search for HeLa cell line - a common and well-documented cell line
    query = "name:HeLa"

    # Act
    result = await client.search_cell_lines(query, page_size=5)

    # Assert
    assert isinstance(result, CellosaurusSearchResult), (
        "Return value should be a CellosaurusSearchResult"
    )
    assert result.total_count > 0, "Should return at least one result for 'HeLa'"
    assert len(result.cell_lines) > 0, "Should return cell line details"

    # Check that returned cell lines contain HeLa in their name
    found_hela = False
    for cell_line in result.cell_lines:
        if "HeLa" in cell_line.name:
            found_hela = True
            break

    assert found_hela, "Results should include a cell line with 'HeLa' in the name"
