from typing import List
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest

from app.api.corefuncs import create_new_user, delete_user, get_users, update_user
from app.database.enums import UserRole
from app.database.models.user import User
from app.datamodels.schemas.request import UserRequestModel
from tests.mocks import MOCK_USER_1


@pytest.mark.asyncio
async def test_create_new_user() -> None:
    """
    Test the creation of a new user by mocking a database session
    and user form, then verifying the result.
    """
    session_mock = AsyncMock()
    user_form_mock = UserRequestModel(**MOCK_USER_1)
    result: User = await create_new_user(session=session_mock, user_form=user_form_mock)
    assert result


@pytest.mark.asyncio
async def test_delete_user() -> None:
    """
    Test the deletion of a user by mocking a database session
    and verifying the result after invoking the delete_user function.
    """
    # create a MagicMock for the session
    session_mock: MagicMock = MagicMock()
    # mock the behavior of the session's query method
    query_mock: MagicMock = AsyncMock()
    session_mock.query.one_or_none.return_value = query_mock
    result: UUID = await delete_user(session=session_mock, user_guid=uuid4())
    assert result
    # assert query method called with expected arguments
    session_mock.query.assert_called_once_with(User)


@pytest.mark.asyncio
async def test_update_user() -> None:
    """
    Test the updating of a user by mocking a user form, database session,
    and verifying the result after updating fields.
    """
    user_form_mock = UserRequestModel(**MOCK_USER_1)
    # mock update fields
    user_form_updated_mock = UserRequestModel(**MOCK_USER_1)
    user_form_updated_mock.role = UserRole.viewer
    # create a MagicMock for the session
    session_mock: MagicMock = MagicMock()
    # mock the behavior of the session's query method
    query_mock: MagicMock = AsyncMock()
    session_mock.query.one_or_none.return_value = query_mock
    result: UUID = await update_user(
        session=session_mock, user_guid=uuid4(), user_form=user_form_updated_mock
    )
    assert result
    assert user_form_mock.role != user_form_updated_mock.role
    # assert query method called with expected arguments
    session_mock.query.assert_called_once_with(User)


@pytest.mark.asyncio
async def test_get_users() -> None:
    """
    Test fetching users by mocking a database session and query,
    then verifying the result.
    """
    # create a MagicMock for the session
    session_mock: MagicMock = MagicMock()
    # mock the behavior of the session's query method
    query_mock: MagicMock = AsyncMock()
    session_mock.query.limit.offset.return_value = query_mock
    result: List[User] = await get_users(session=session_mock)
    assert result
