from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Body, Depends, Path
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette import status

from app.api import corefuncs
from app.api.decorators import cache_result, manage_transaction, role_checker
from app.database.enums import UserRole
from app.database.models.user import User
from app.database.session import get_db
from app.datamodels.schemas.auth import Token
from app.datamodels.schemas.request import UserRequestBaseModel, UserRequestModel
from app.datamodels.schemas.response import UserResponseModel
from app.depends.auth import get_current_user, login_for_access_token

router = APIRouter(prefix="/users")


@router.get(
    path="",
    description="Get all users",
    status_code=status.HTTP_200_OK,
    response_model=List[UserResponseModel],
)
@role_checker(role_levels=(UserRole.admin, UserRole.viewer))
@cache_result(key="users", ttl=3600)
async def get_users(
    session_user: Annotated[User, Depends(dependency=get_current_user)],
    session: Annotated[Session, Depends(dependency=get_db)],
) -> List[User]:
    """
    Retrieve all users from the database.

    Args:
        :session_user (User): The current logged user.
        :session (Session): The SQLAlchemy database session.

    Returns:
        :List[User]: A list of user objects retrieved from the database.
    """
    return await corefuncs.get_users(session=session)


@router.post(
    path="/create",
    description="Create new user",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponseModel,
)
@manage_transaction
async def create_new_user(
    user_form: Annotated[UserRequestModel, Body(default=...)],
    session: Annotated[Session, Depends(dependency=get_db)],
) -> User:
    """
    Endpoint to create a new user.

    Args:
        :user_form (UserRequestModel): The request model containing user data.
        :session (Session): The SQLAlchemy database session.

    Returns:
        :UserResponseModel: The response model containing the created user data.
    """
    return await corefuncs.create_new_user(session=session, user_form=user_form)


@router.patch(
    path="/{user_guid}",
    description="Update existing user",
    status_code=status.HTTP_200_OK,
    response_model=UserResponseModel,
)
@role_checker(role_levels=(UserRole.admin,))
@manage_transaction
async def update_user(
    user_guid: Annotated[UUID, Path(default=...)],
    user_form: Annotated[UserRequestBaseModel, Body(default=...)],
    session_user: Annotated[User, Depends(dependency=get_current_user)],
    session: Annotated[Session, Depends(dependency=get_db)],
) -> User:
    """
    Update an existing user in the database.

    Args:
        :user_guid (UUID): The GUID related to the user row to be updated.
        :user_form (UserRequestBaseModel): The request model containing the updated user data.
        :session_user (User): The current logged user.
        :session (Session): The SQLAlchemy database session.

    Returns:
        :User: The updated user object.
    """
    return await corefuncs.update_user(
        session=session, user_guid=user_guid, user_form=user_form
    )


@router.delete(
    path="/{user_guid}",
    description="Delete existing user",
    status_code=status.HTTP_202_ACCEPTED,
)
@role_checker(role_levels=(UserRole.admin,))
@manage_transaction
async def delete_user(
    user_guid: Annotated[UUID, Path(default=...)],
    session_user: Annotated[User, Depends(dependency=get_current_user)],
    session: Annotated[Session, Depends(dependency=get_db)],
) -> UUID:
    """
    Delete an existing user from the database.

    Args:
        :user_guid (UUID): The GUID related to the user row to be deleted.
        :session_user (User): The current logged user.
        :session (Session): The SQLAlchemy database session.

    Returns:
        :UUID: The UUID of the deleted user.
    """
    return await corefuncs.delete_user(session=session, user_guid=user_guid)


@router.post(
    path="/token",
    description="Get token from login",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=Token,
)
@manage_transaction
async def get_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[Session, Depends(dependency=get_db)],
) -> Token:
    """
    Get access token from login credentials.

    Args:
        :form_data (OAuth2PasswordRequestForm): The login credentials provided by the user.
        :session (Session): The SQLAlchemy database session.

    Returns:
        :Token: The access token for the authenticated user.
    """
    return await login_for_access_token(session=session, form_data=form_data)
