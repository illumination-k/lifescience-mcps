from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_message import ErrorMessage
from ...models.fields import Fields
from ...models.format_ import Format
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    q: Union[Unset, str] = "id:HeLa",
    start: Union[Unset, int] = 0,
    rows: Union[Unset, int] = 1000,
    format_: Union[Unset, Format] = UNSET,
    fld: Union[Unset, list[Fields]] = UNSET,
    fields: Union[Unset, str] = UNSET,
    sort: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["q"] = q

    params["start"] = start

    params["rows"] = rows

    json_format_: Union[Unset, str] = UNSET
    if not isinstance(format_, Unset):
        json_format_ = format_.value

    params["format"] = json_format_

    json_fld: Union[Unset, list[str]] = UNSET
    if not isinstance(fld, Unset):
        json_fld = []
        for fld_item_data in fld:
            fld_item = fld_item_data.value
            json_fld.append(fld_item)

    params["fld"] = json_fld

    params["fields"] = fields

    params["sort"] = sort

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/search/cell-line",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, ErrorMessage, HTTPValidationError]]:
    if response.status_code == 200:
        response_200 = response.json()
        return response_200
    if response.status_code == 400:
        response_400 = ErrorMessage.from_dict(response.json())

        return response_400
    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, ErrorMessage, HTTPValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    q: Union[Unset, str] = "id:HeLa",
    start: Union[Unset, int] = 0,
    rows: Union[Unset, int] = 1000,
    format_: Union[Unset, Format] = UNSET,
    fld: Union[Unset, list[Fields]] = UNSET,
    fields: Union[Unset, str] = UNSET,
    sort: Union[Unset, str] = UNSET,
) -> Response[Union[Any, ErrorMessage, HTTPValidationError]]:
    """Search Cell Lines

    Args:
        q (Union[Unset, str]): Search query string using Solr synax. Example: 'id:Hela' Default:
            'id:HeLa'.
        start (Union[Unset, int]): Index of first item to retrieve in the search result list. See
            also <i>start</i> parameter in Solr syntax. Default: 0.
        rows (Union[Unset, int]): Number of items to retrieve from the search result list. See
            also <i>rows</i> in Solr synax, Example: '10' Default: 1000.
        format_ (Union[Unset, Format]):
        fld (Union[Unset, list[Fields]]): Optional list of fields to return in the response.
                        All the fields are returned in the response if undefined.
                        Values passed in parameter <i>fld</i> takes precedence over values passed in
            parameter <i>fields</i>.
                        More information on content of fields <a href="help-fields">here</a>.

        fields (Union[Unset, str]): Optional list of fields to return in the response.
                        <i>fields</i> value is a comma-separated list of field tags or field
            shortnames.
                        Examples: 'id,ac,sy,cc', 'id,ac,ox'.
                        All the fields are returned if undefined.
                        Values passed in parameter <i>fld</i> takes precedence over values passed in
            parameter <i>fields</i>.
                        More information on fields <a href="help-fields">here</a>.

        sort (Union[Unset, str]): Optional field(s) determining the sort order of the search
            result.
                        Every field name must be followed with a space and the sort direction
            (ASCending or DESCending).
                        When multiple fields are used as the value of this parameter, they must be
            separated by a comma.
                        Example: 'group asc,derived-from-site desc'
                        All the fields described <a href="help-fields">here</a> in are sortable.
                        When this parameter is undefined, the search result rows are sorted by
            relevance.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ErrorMessage, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        q=q,
        start=start,
        rows=rows,
        format_=format_,
        fld=fld,
        fields=fields,
        sort=sort,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    q: Union[Unset, str] = "id:HeLa",
    start: Union[Unset, int] = 0,
    rows: Union[Unset, int] = 1000,
    format_: Union[Unset, Format] = UNSET,
    fld: Union[Unset, list[Fields]] = UNSET,
    fields: Union[Unset, str] = UNSET,
    sort: Union[Unset, str] = UNSET,
) -> Optional[Union[Any, ErrorMessage, HTTPValidationError]]:
    """Search Cell Lines

    Args:
        q (Union[Unset, str]): Search query string using Solr synax. Example: 'id:Hela' Default:
            'id:HeLa'.
        start (Union[Unset, int]): Index of first item to retrieve in the search result list. See
            also <i>start</i> parameter in Solr syntax. Default: 0.
        rows (Union[Unset, int]): Number of items to retrieve from the search result list. See
            also <i>rows</i> in Solr synax, Example: '10' Default: 1000.
        format_ (Union[Unset, Format]):
        fld (Union[Unset, list[Fields]]): Optional list of fields to return in the response.
                        All the fields are returned in the response if undefined.
                        Values passed in parameter <i>fld</i> takes precedence over values passed in
            parameter <i>fields</i>.
                        More information on content of fields <a href="help-fields">here</a>.

        fields (Union[Unset, str]): Optional list of fields to return in the response.
                        <i>fields</i> value is a comma-separated list of field tags or field
            shortnames.
                        Examples: 'id,ac,sy,cc', 'id,ac,ox'.
                        All the fields are returned if undefined.
                        Values passed in parameter <i>fld</i> takes precedence over values passed in
            parameter <i>fields</i>.
                        More information on fields <a href="help-fields">here</a>.

        sort (Union[Unset, str]): Optional field(s) determining the sort order of the search
            result.
                        Every field name must be followed with a space and the sort direction
            (ASCending or DESCending).
                        When multiple fields are used as the value of this parameter, they must be
            separated by a comma.
                        Example: 'group asc,derived-from-site desc'
                        All the fields described <a href="help-fields">here</a> in are sortable.
                        When this parameter is undefined, the search result rows are sorted by
            relevance.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ErrorMessage, HTTPValidationError]
    """

    return sync_detailed(
        client=client,
        q=q,
        start=start,
        rows=rows,
        format_=format_,
        fld=fld,
        fields=fields,
        sort=sort,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    q: Union[Unset, str] = "id:HeLa",
    start: Union[Unset, int] = 0,
    rows: Union[Unset, int] = 1000,
    format_: Union[Unset, Format] = UNSET,
    fld: Union[Unset, list[Fields]] = UNSET,
    fields: Union[Unset, str] = UNSET,
    sort: Union[Unset, str] = UNSET,
) -> Response[Union[Any, ErrorMessage, HTTPValidationError]]:
    """Search Cell Lines

    Args:
        q (Union[Unset, str]): Search query string using Solr synax. Example: 'id:Hela' Default:
            'id:HeLa'.
        start (Union[Unset, int]): Index of first item to retrieve in the search result list. See
            also <i>start</i> parameter in Solr syntax. Default: 0.
        rows (Union[Unset, int]): Number of items to retrieve from the search result list. See
            also <i>rows</i> in Solr synax, Example: '10' Default: 1000.
        format_ (Union[Unset, Format]):
        fld (Union[Unset, list[Fields]]): Optional list of fields to return in the response.
                        All the fields are returned in the response if undefined.
                        Values passed in parameter <i>fld</i> takes precedence over values passed in
            parameter <i>fields</i>.
                        More information on content of fields <a href="help-fields">here</a>.

        fields (Union[Unset, str]): Optional list of fields to return in the response.
                        <i>fields</i> value is a comma-separated list of field tags or field
            shortnames.
                        Examples: 'id,ac,sy,cc', 'id,ac,ox'.
                        All the fields are returned if undefined.
                        Values passed in parameter <i>fld</i> takes precedence over values passed in
            parameter <i>fields</i>.
                        More information on fields <a href="help-fields">here</a>.

        sort (Union[Unset, str]): Optional field(s) determining the sort order of the search
            result.
                        Every field name must be followed with a space and the sort direction
            (ASCending or DESCending).
                        When multiple fields are used as the value of this parameter, they must be
            separated by a comma.
                        Example: 'group asc,derived-from-site desc'
                        All the fields described <a href="help-fields">here</a> in are sortable.
                        When this parameter is undefined, the search result rows are sorted by
            relevance.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ErrorMessage, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        q=q,
        start=start,
        rows=rows,
        format_=format_,
        fld=fld,
        fields=fields,
        sort=sort,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    q: Union[Unset, str] = "id:HeLa",
    start: Union[Unset, int] = 0,
    rows: Union[Unset, int] = 1000,
    format_: Union[Unset, Format] = UNSET,
    fld: Union[Unset, list[Fields]] = UNSET,
    fields: Union[Unset, str] = UNSET,
    sort: Union[Unset, str] = UNSET,
) -> Optional[Union[Any, ErrorMessage, HTTPValidationError]]:
    """Search Cell Lines

    Args:
        q (Union[Unset, str]): Search query string using Solr synax. Example: 'id:Hela' Default:
            'id:HeLa'.
        start (Union[Unset, int]): Index of first item to retrieve in the search result list. See
            also <i>start</i> parameter in Solr syntax. Default: 0.
        rows (Union[Unset, int]): Number of items to retrieve from the search result list. See
            also <i>rows</i> in Solr synax, Example: '10' Default: 1000.
        format_ (Union[Unset, Format]):
        fld (Union[Unset, list[Fields]]): Optional list of fields to return in the response.
                        All the fields are returned in the response if undefined.
                        Values passed in parameter <i>fld</i> takes precedence over values passed in
            parameter <i>fields</i>.
                        More information on content of fields <a href="help-fields">here</a>.

        fields (Union[Unset, str]): Optional list of fields to return in the response.
                        <i>fields</i> value is a comma-separated list of field tags or field
            shortnames.
                        Examples: 'id,ac,sy,cc', 'id,ac,ox'.
                        All the fields are returned if undefined.
                        Values passed in parameter <i>fld</i> takes precedence over values passed in
            parameter <i>fields</i>.
                        More information on fields <a href="help-fields">here</a>.

        sort (Union[Unset, str]): Optional field(s) determining the sort order of the search
            result.
                        Every field name must be followed with a space and the sort direction
            (ASCending or DESCending).
                        When multiple fields are used as the value of this parameter, they must be
            separated by a comma.
                        Example: 'group asc,derived-from-site desc'
                        All the fields described <a href="help-fields">here</a> in are sortable.
                        When this parameter is undefined, the search result rows are sorted by
            relevance.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ErrorMessage, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            client=client,
            q=q,
            start=start,
            rows=rows,
            format_=format_,
            fld=fld,
            fields=fields,
            sort=sort,
        )
    ).parsed
