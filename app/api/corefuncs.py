from typing import List
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import Column
from sqlalchemy.orm import Session
from starlette import status

from app.api.constants import GET_USERS_REDIS_K
from app.api.utils import invalidate_cache
from app.database import crud
from app.database.cache import redis
from app.database.models.user import User
from app.datamodels.schemas.request import UserRequestBaseModel, UserRequestModel
from app.depends.auth import pwd_context


async def create_new_user(session: Session, user_form: UserRequestModel) -> User:
    """
    Create a new user in the database.

    Args:
        :session (Session): The SQLAlchemy database session.
        :user_form (UserRequestModel): The request model containing user data.

    Returns:
        :User: The newly created user object.

    Description:
        This function creates a new user in the database using the provided user form data.
        It performs the following steps:
            1. Constructs a new User object using the data from the user form.
            2. Converts the user's first_name and last first_name to lowercase.
            3. Hashes the user's password using the configured password hashing algorithm.
            4. Adds the user to the database session.
            5. Deletes the cached users data from the Redis cache to ensure updated data retrieval.
    """
    user = User(**user_form.model_dump())
    user.first_name = user.first_name.lower()
    user.last_name = user.last_name.lower()
    user.hashed_psw = pwd_context.hash(secret=user.hashed_psw)
    crud.add_user(session=session, user=user)

    # invalidate cache
    await invalidate_cache(redis=redis, key=GET_USERS_REDIS_K, as_pattern=True)
    return user


async def delete_user(session: Session, user_guid: UUID) -> UUID:
    """
    Delete a user from the database based on their GUID.

    Args:
        :session (Session): The SQLAlchemy database session.
        :user_guid (UUID): The GUID related to the user row to be deleted.

    Returns:
        :UUID: The GUID related to the deleted user row.

    Raises:
        :HTTPException: If the user with the specified GUID is not found in the database.

    Description:
        This function deletes a user from the database based on their GUID.
        It performs the following steps:
            1. Queries the database to find the user with the specified GUID.
            2. If the user is not found, raises an HTTPException with status code 404.
            3. Deletes the user from the database using the `crud.delete_user` function.
            4. Deletes the cached users data from the Redis cache using the `invalidate_cache` function.
    """
    deletable_user: User | None = crud.find_user(
        session=session, criteria=(Column("guid") == user_guid,)
    )
    if not deletable_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with guid '{user_guid}' not found",
        )
    crud.delete_user(session=session, user=deletable_user)

    # invalidate cache
    await invalidate_cache(redis=redis, key=GET_USERS_REDIS_K, as_pattern=True)
    return user_guid


async def update_user(
    session: Session, user_guid: UUID, user_form: UserRequestBaseModel
) -> User:
    """
    Update an existing user in the database.

    Args:
        :session (Session): The SQLAlchemy database session.
        :user_guid (UUID): The GUID related to the user row to be updated.
        :user_form (UserRequestBaseModel): The request model containing updated user data.

    Returns:
        :User: The updated user object.

    Raises:
        :HTTPException: If the specified user is not found in the database.

    Description:
        This function updates an existing user in the database with the provided user data.
        It performs the following steps:
            1. Queries the database to find the user with the specified UUID, acquiring a row-level lock.
            2. Raises an HTTPException with status code 404 if no user is found.
            3. Updates the user object with the new data from the user form.
            4. Commits the transaction to persist the changes in the database.
            5. Deletes the cached users data from the Redis cache.
    """
    updatable_user: User | None = (
        session.query(User)
        .filter(User.guid == user_guid)
        .with_for_update()
        .one_or_none()
    )
    if not updatable_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with guid '{user_guid}' not found",
        )

    for k, v in user_form.model_dump().items():
        setattr(updatable_user, k, v)

    crud.update_user(session=session, user=updatable_user)

    # invalidate cache
    await invalidate_cache(redis=redis, key=GET_USERS_REDIS_K, as_pattern=True)
    return updatable_user


async def get_users(session: Session, offset: int = 0, limit: int = 100) -> List[User]:
    """
    Retrieve a list of users from the database with optional pagination.

    Args:
        :session (Session): The SQLAlchemy database session.
        :offset (int, optional): The offset from which to start fetching users. Default is 0.
        :limit (int, optional): The maximum number of users to retrieve. Default is 100.

    Returns:
        :List[User]: A list of user objects retrieved from the database.

    Description:
        This function retrieves a list of users from the database using the provided database session.
        Optionally, it allows pagination by specifying the starting offset and the maximum number of users to retrieve.
        It delegates the database query to the `crud.find_users` function, which executes the query and returns
        the list of users.
    """
    return crud.find_users(session=session, offset=offset, limit=limit)
