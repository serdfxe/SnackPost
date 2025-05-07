from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.user_response_dto import UserResponseDTO
from ...types import Response


def _get_kwargs(
    *,
    x_user_id: int,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["x-user-id"] = str(x_user_id)

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/user/",
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, HTTPValidationError, UserResponseDTO]]:
    if response.status_code == 200:
        response_200 = UserResponseDTO.from_dict(response.json())

        return response_200
    if response.status_code == 404:
        response_404 = cast(Any, None)
        return response_404
    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, HTTPValidationError, UserResponseDTO]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    x_user_id: int,
) -> Response[Union[Any, HTTPValidationError, UserResponseDTO]]:
    """Get User Route

     Get user data. The operation returns the data of the user that is associated with the provided
    X-User-Id.

    Args:
        x_user_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, HTTPValidationError, UserResponseDTO]]
    """

    kwargs = _get_kwargs(
        x_user_id=x_user_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    x_user_id: int,
) -> Optional[Union[Any, HTTPValidationError, UserResponseDTO]]:
    """Get User Route

     Get user data. The operation returns the data of the user that is associated with the provided
    X-User-Id.

    Args:
        x_user_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, HTTPValidationError, UserResponseDTO]
    """

    return sync_detailed(
        client=client,
        x_user_id=x_user_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    x_user_id: int,
) -> Response[Union[Any, HTTPValidationError, UserResponseDTO]]:
    """Get User Route

     Get user data. The operation returns the data of the user that is associated with the provided
    X-User-Id.

    Args:
        x_user_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, HTTPValidationError, UserResponseDTO]]
    """

    kwargs = _get_kwargs(
        x_user_id=x_user_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    x_user_id: int,
) -> Optional[Union[Any, HTTPValidationError, UserResponseDTO]]:
    """Get User Route

     Get user data. The operation returns the data of the user that is associated with the provided
    X-User-Id.

    Args:
        x_user_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, HTTPValidationError, UserResponseDTO]
    """

    return (
        await asyncio_detailed(
            client=client,
            x_user_id=x_user_id,
        )
    ).parsed
