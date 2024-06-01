import json
import traceback
from functools import wraps
from typing import Any, Callable, List, Tuple

from fastapi import Request
from fastapi.exceptions import HTTPException
from psycopg2.errors import UniqueViolation
from redis.commands.core import ResponseT
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette import status

from app.configlog import logger
from app.database.cache import redis
from app.database.enums import UserRole
from app.database.models.user import User
from app.datamodels.schemas.response import UserResponseModel

CONN = "session"


def manage_transaction(func: Callable) -> Any:
    """
    Decorator for managing database transactions.

    Args:
        :func (Callable): The function to be decorated.

    Returns:
        :Any: The result of the decorated function.

    Raises:
        :HTTPException: HTTP exceptions with appropriate status codes and details.
        "Exception: Any other unexpected exception with status code 500.

    Description:
        This decorator manages database transactions for the decorated function.
        It performs the following steps:
            1. Retrieves the SQLAlchemy session from the keyword arguments.
            2. Wraps the decorated function with a try-except block to handle exceptions.
            3. Begins a transaction using the SQLAlchemy session.
            4. Calls the decorated function with the provided arguments and keyword arguments.
            5. Commits the transaction if the function execution is successful.
            6. Rolls back the transaction and raises an appropriate HTTPException if an error occurs.
            7. Closes the SQLAlchemy session after handling the transaction.
    """

    @wraps(wrapped=func)
    async def wrapper(*args, **kwargs) -> Any:
        _session: Session = kwargs[CONN]
        try:
            with _session:
                rv: Any = await func(*args, **kwargs)
                _session.expunge_all()
                _session.flush()
                _session.commit()
                return rv
        except (ValueError, TypeError) as e:
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=e.args,
            )
        except (IntegrityError, UniqueViolation) as e:
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=e.args,
            )
        except KeyError as e:
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=e.args,
            )
        except HTTPException as e:
            logger.error(traceback.format_exc())
            raise e
        except Exception as e:
            logger.error(traceback.format_exc())
            _session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=e.args,
            )
        finally:
            _session.close()

    return wrapper


def cache_result(key: str, ttl: int) -> Any:
    """
    Decorator function to cache the result of an asynchronous function.

    Args:
        :key (str): The base key under which to cache the result. This key will be combined with offset and limit.
        :ttl (int): The time-to-live (TTL) duration for the cached result, in seconds.

    Returns:
        :Callable: A decorator function.

    Raises:
        :HTTPException: If an HTTP exception occurs during function execution.
        :Exception: If an unexpected exception occurs during function execution.

    Description:
        This decorator function caches the result of the decorated asynchronous function.
        It performs the following steps:
            1. Checks if the result is cached using the provided cache key combined with offset and limit.
            2. If the result is cached, returns the cached result.
            3. If the result is not cached, computes the result by calling the decorated function.
            4. Converts the SQLAlchemy ORM instances returned by the decorated function to Pydantic models.
            5. Caches the result using the provided cache key combined with offset and limit.
            6. Returns the computed result.
    """

    def decorator(func: Callable) -> Any:
        @wraps(wrapped=func)
        async def wrapper(*args, **kwargs) -> Any:
            try:
                cache_key = key
                if kwargs.get("request"):
                    request: Request = kwargs["request"]
                    # extract offset and limit from query parameters
                    offset: str | int = request.query_params.get("offset", default=0)
                    limit: str | int = request.query_params.get("limit", default=100)
                    cache_key: str = f"{key}_offset_{offset}_limit_{limit}"

                # check if the result is cached
                cached: ResponseT = redis.get(name=cache_key)
                if cached is not None:
                    return json.loads(s=cached)
                # compute the result
                func_result: List[User] = await func(*args, **kwargs)

                # parsing sqlalchemy ORM instances to pydantic models
                models: List[UserResponseModel] = [
                    UserResponseModel(**user.dump()) for user in func_result
                ]
                # cache the result
                redis.setex(
                    name=cache_key,
                    time=ttl,
                    value=json.dumps([m.model_dump() for m in models]),
                )
                return models
            except HTTPException as e:
                raise e
            except Exception as e:
                logger.error(traceback.format_exc())
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
                )

        return wrapper

    return decorator


def role_checker(role_levels: Tuple[UserRole, ...]) -> Any:
    """
    Decorator function for role-based access control (RBAC) enforcement.

    Args:
        :role_levels (Tuple[UserRole, ...]): Tuple of user roles allowed.

    Returns:
        :Any: The decorated function.

    Raises:
        :HTTPException: If the session user's role is not authorized to access the function.
        :Exception: If any other exception occurs during function execution.

    Description:
        This decorator function performs role-based access control (RBAC) enforcement
        for the decorated function. It restricts access to users with roles specified
        in the `role_levels` argument.

        If the session user's role is not authorized to access the function, an HTTPException
        with status code 401 (Unauthorized) is raised.

        If any other exception occurs during function execution, it is logged, and the
        original exception is re-raised.
    """

    def decorator(func: Callable) -> Any:
        @wraps(wrapped=func)
        async def wrapper(*args, **kwargs) -> Any:
            try:
                session_user: User | None = kwargs.get("session_user")
                # check permissions
                if session_user:
                    if session_user.role not in role_levels:
                        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Not authorized",
                        )
                func_result: Any = await func(*args, **kwargs)
                return func_result
            except HTTPException as e:
                raise e
            except Exception as e:
                logger.error(traceback.format_exc())
                raise e

        return wrapper

    return decorator
