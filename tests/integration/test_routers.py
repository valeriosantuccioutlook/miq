from datetime import timedelta
from typing import Any, Generator
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from httpx import Response
from sqlalchemy.orm import Session
from starlette import status

from app.database.models.user import User
from app.depends.auth import create_auth_token
from tests.mocks import MOCK_USER_1, MOCK_USER_3


@pytest.fixture
def get_current_user_mock(
    mock_auth_user: User,
) -> Generator[MagicMock | AsyncMock, Any, None]:
    with patch("app.depends.auth.get_current_user") as mock:
        mock.return_value = mock_auth_user
        yield mock


@pytest.fixture
def get_db_mock() -> Generator[MagicMock | AsyncMock, Any, None]:
    with patch("app.database.session.get_db") as mock:
        mock.return_value = MagicMock(spec=Session)
        yield mock


@pytest.fixture
def crud_find_user(mock_auth_user: User) -> Generator[MagicMock | AsyncMock, Any, None]:
    with patch("app.database.crud.find_user") as mock:
        mock.return_value = mock_auth_user
        yield mock


@pytest.fixture
def corefuncs_create_user() -> Generator[MagicMock | AsyncMock, Any, None]:
    with patch("app.api.corefuncs.create_new_user") as mock:
        mock.return_value = MOCK_USER_1
        yield mock


@pytest.fixture
def corefuncs_delete_user() -> Generator[MagicMock | AsyncMock, Any, None]:
    with patch("app.api.corefuncs.delete_user") as mock:
        mock.return_value = MOCK_USER_3["guid"]
        yield mock


async def mock_access_token(
    mock_auth_user: User,
) -> str:
    return await create_auth_token(
        data={"sub": mock_auth_user.email, "user_guid": str(mock_auth_user.guid)},
        expires_delta=timedelta(hours=24),
    )


@pytest.mark.asyncio
async def test_get_users(
    client: TestClient,
    mock_auth_user: User,
    get_current_user_mock: User,
    crud_find_user: User,
    get_db_mock: Session,
) -> None:
    """
    Test the retrieval of users by simulating an authenticated request
    and asserting an empty user list response.
    """
    # get token for auth user
    auth_token: str = await mock_access_token(mock_auth_user=mock_auth_user)
    # make request with mocked access token
    response: Response = client.get(
        url="/users", headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


@pytest.mark.asyncio
async def test_create_user(
    client: TestClient,
    mock_auth_user: User,
    get_current_user_mock: User,
    crud_find_user: User,
    get_db_mock: Session,
    corefuncs_create_user: User,
    # crud_add_user: User,
) -> None:
    """
    Test the user creation endpoint by simulating a request with authentication,
    verifying successful creation, and checking the returned user email.
    """
    # get token for auth user
    auth_token: str = await mock_access_token(mock_auth_user=mock_auth_user)
    # make request with mocked access token
    response: Response = client.post(
        url="/users/create",
        headers={"Authorization": f"Bearer {auth_token}"},
        json=MOCK_USER_1,
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["email"] == MOCK_USER_1["email"]


@pytest.mark.asyncio
async def test_delete_user(
    client: TestClient,
    mock_auth_user: User,
    get_current_user_mock: User,
    crud_find_user: User,
    get_db_mock: Session,
    corefuncs_delete_user: UUID,
) -> None:
    """
    Test the deletion of a user by simulating an authenticated request
    and verifying the response status code and content.
    """
    # get token for auth user
    auth_token: str = await mock_access_token(mock_auth_user=mock_auth_user)
    # make request with mocked access token
    response: Response = client.delete(
        url=f"/users/{MOCK_USER_3["guid"]}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.json() == str(MOCK_USER_3["guid"])
