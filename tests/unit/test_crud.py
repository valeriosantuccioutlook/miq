from typing import List
from unittest.mock import MagicMock

from sqlalchemy import Column
from sqlalchemy.orm import Query, Session
from sqlalchemy.sql.elements import ColumnElement

from app.database import crud
from app.database.models.user import User
from tests.mocks import MOCK_USER_1, MOCK_USER_2


def test_find_user_with_criteria() -> None:
    """
    Test finding a user with specified criteria by mocking a database session
    and query object, then verifying the result.
    """
    # define a test session
    session_mock = MagicMock()
    # mock behavior of query object
    query_mock = MagicMock(spec=Query)
    # mock behavior of filter and one_or_none methods
    query_mock.filter.return_value = query_mock
    query_mock.one_or_none.return_value = MOCK_USER_1
    # set query_mock as the return value of the session's query method
    session_mock.query.return_value = query_mock

    criteria: tuple[ColumnElement[bool]] = (Column("email") == MOCK_USER_1["email"],)
    result: User | None = crud.find_user(session=session_mock, criteria=criteria)

    assert result == MOCK_USER_1

    # assert query method called with expected arguments
    session_mock.query.assert_called_once_with(User)
    query_mock.filter.assert_called_once_with(*criteria)
    query_mock.one_or_none.assert_called_once()


def test_find_users_default_pagination() -> None:
    """
    Test finding users with default pagination by mocking session and query behavior,
    verifying the result matches expected users.
    """
    # define a test session
    session_mock = MagicMock()
    # mock behavior of query object
    query_mock = MagicMock(spec=Query)
    # mock behavior of filter and one_or_none methods
    query_mock.offset.return_value.limit.return_value.all.return_value = [
        MOCK_USER_1,
        MOCK_USER_2,
    ]

    # set query_mock as the return value of the session's query method
    session_mock.query.return_value = query_mock

    result: List[User] = crud.find_users(session=session_mock)
    assert result == [MOCK_USER_1, MOCK_USER_2]

    # assert query method called with expected arguments
    session_mock.query.assert_called_once_with(User)
    query_mock.offset.assert_called_once_with(offset=0)


def test_find_users_custom_offset() -> None:
    """
    Test the custom offset functionality for finding users
    by mocking a session and verifying the offset result.
    """
    # define a test session
    session_mock = MagicMock()
    # mock behavior of query object
    query_mock = MagicMock(spec=Query)
    # mock behavior of filter and one_or_none methods
    query_mock.offset.return_value.limit.return_value.all.return_value = [
        MOCK_USER_1,
        MOCK_USER_2,
    ]
    # set query_mock as the return value of the session's query method
    session_mock.query.return_value = query_mock

    custom_offset = 10
    result: List[User] = crud.find_users(session=session_mock, offset=custom_offset)

    assert result == [MOCK_USER_1, MOCK_USER_2]

    # assert query method called with expected arguments
    session_mock.query.assert_called_once_with(User)
    query_mock.offset.assert_called_once_with(offset=custom_offset)


def test_add_user() -> None:
    """
    Test the addition of a user to the database session,
    verifying that the user object is correctly added.
    """
    # define a test session
    session_mock = MagicMock(spec=Session)
    # create a mock user object
    user_mock = MagicMock(spec=User)

    crud.add_user(session=session_mock, user=user_mock)

    # assert user object added to the session
    session_mock.add.assert_called_once_with(instance=user_mock)
    session_mock.flush.assert_called_once()


def test_delete_user() -> None:
    """
    Test the deletion of a user by mocking a database session and user object,
    then verifying the deletion operation.
    """
    # define a test session
    session_mock = MagicMock()
    # create a mock user object
    test_user = User()

    crud.delete_user(session=session_mock, user=test_user)

    # assert delete method called on the session with test user
    session_mock.delete.assert_called_once_with(instance=test_user)
    session_mock.flush.assert_called_once()
