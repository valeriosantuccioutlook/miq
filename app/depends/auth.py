from datetime import datetime, timedelta
from typing import Annotated, Any, Dict, Literal

import pytz
from fastapi import Depends
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import Column
from sqlalchemy.orm import Session
from starlette import status

from app.database import crud
from app.database.cache import redis
from app.database.models.user import User
from app.database.session import get_db
from app.datamodels.schemas.auth import DecodedCredentials, Token, TokenData
from app.settings import settings

# set env and OAuth2 schema
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def verify_token(
    token: str,
) -> DecodedCredentials:
    """
    Verify and decode an authentication token.

    Args:
        :token (str): The authentication token to verify and decode.

    Returns:
        :DecodedCredentials: A model containing the decoded token payload.

    Raises:
        :HTTPException: Raised when the token is invalid or expired.

    Description:
        This function verifies the authenticity and integrity of the provided authentication token.
        It performs the following steps:
            1. Decodes the token using the configured secret key and algorithm.
            2. Constructs a `DecodedCredentials` object from the decoded token payload.
            3. Returns the decoded credentials if the token is valid.
            4. Raises an HTTPException with a status code of 401 Unauthorized if the token is invalid or expired.
    """
    try:
        decoded: Dict[str, Any] = jwt.decode(
            token=token, key=settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return DecodedCredentials(**decoded)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token"
        )


async def get_current_user(
    token: Annotated[str, Depends(dependency=oauth2_scheme)],
    session: Session = Depends(dependency=get_db),
) -> User:
    """
    Get the current user based on the provided authentication token.

    Args:
        :token (str): The authentication token obtained from the request headers.
        :session (Session, optional): The SQLAlchemy database session. Defaults to Depends(dependency=get_db).

    Returns:
        :User: The user corresponding to the provided authentication token.

    Raises:
        :HTTPException: An exception indicating authentication failure.
            This could occur due to invalid credentials or missing user data.

    Description:
        This function validates the provided authentication token and retrieves the corresponding user from the database.
        It performs the following steps:
            1. Verifies the token's validity and extracts the user's email from the token payload.
            2. Retrieves the user from the database based on the email address obtained from the token.
            3. Raises an HTTPException with status code 401 (Unauthorized) if the token cannot be validated,
            if the email is missing from the token payload, or if no user is found with the specified email.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        credentials: DecodedCredentials = await verify_token(token=token)
        if credentials.email is None:
            raise credentials_exception
        TokenData(email=credentials.email)
    except JWTError:
        raise credentials_exception
    user: User | None = crud.find_user(
        session=session, criteria=(Column("email") == credentials.email,)
    )
    if user is None:
        raise credentials_exception
    return user


async def create_auth_token(
    data: dict,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Create an authentication token.

    Args:
        :data (dict): The data payload to include in the token.
        :expires_delta (timedelta, optional): The expiration delta for the token.
            If provided, the token will expire after the specified duration.
            Defaults to None, in which case a default expiration of 15 minutes is used.

    Returns:
        :str: The encoded authentication token as a string.

    Description:
        :This function generates an authentication token using the provided data payload.
        :It optionally sets an expiration time for the token, allowing control over its validity period.
        :The token is encoded using the configured secret key and algorithm defined in the application settings.
    """
    to_encode: Dict[Any, Any] = data.copy()
    if expires_delta:
        expire: datetime = datetime.now(tz=pytz.utc) + expires_delta
    else:
        expire = datetime.now(tz=pytz.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt: str = jwt.encode(
        claims=to_encode, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


async def authenticate_user(
    email: str,
    password: str,
    session: Session = Depends(dependency=get_db),
) -> User | Literal[False]:
    """
    Authenticate a user by verifying the email and password.

    Args:
        :email (str): The email address of the user to authenticate.
        :password (str): The password of the user to authenticate.
        :session (Session, optional): The SQLAlchemy database session.
            Defaults to Depends(dependency=get_db).

    Returns:
        :Union[User, bool]: The authenticated user object if authentication succeeds,
            or False if authentication fails.

    Description:
        This function authenticates a user by verifying the provided email and password.
        It performs the following steps:
            1. Queries the database to find a user with the specified email address.
            2. If no user is found, returns False indicating authentication failure.
            3. Verifies the provided password against the hashed password stored in the database.
            4. If the password verification fails, returns False indicating authentication failure.
            5. If both email and password are valid, returns the authenticated user object.
    """
    user: User | None = crud.find_user(
        session=session, criteria=(Column("email") == email,)
    )
    if user is None:
        return False
    if not pwd_context.verify(secret=password, hash=user.hashed_psw):
        return False
    return user


async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Session = Depends(dependency=get_db),
) -> Token:
    """
    Log in a user and generate an access token for authentication.

    Args:
        :form_data (OAuth2PasswordRequestForm): The form data containing the user's email and password.
        :session (Session, optional): The SQLAlchemy database session. Defaults to Depends(dependency=get_db).

    Returns:
        :Token: An object containing the access token.

    Raises:
        :HTTPException: Raised if the provided credentials are incorrect or if there is an authentication failure.

    Description:
        This function logs in a user by verifying the provided email and password against the database.
        If the credentials are correct, it generates an access token for the user and stores it in Redis for future authentication.

        Steps:
            1. Authenticate the user by calling the `authenticate_user` function.
            2. If authentication fails, raise an HTTPException with status code 401 (Unauthorized).
            3. Generate an access token for the user with an expiration time based on the configured settings.
            4. Store the access token in Redis with a key based on the user's unique identifier.
            5. Return an object containing the access token.
    """
    user: User | Literal[False] = await authenticate_user(
        email=form_data.username, password=form_data.password, session=session
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS)
    access_token: str = await create_auth_token(
        data={"sub": user.email, "user_guid": str(user.guid)},
        expires_delta=access_token_expires,
    )
    redis.setex(
        name=f"{user.guid}_auth_token",
        time=settings.ACCESS_TOKEN_EXPIRE_SECONDS,
        value=access_token,
    )
    return Token(access_token=access_token, token_type="bearer")
