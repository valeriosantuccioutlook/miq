from typing import Iterable, List

from sqlalchemy import BinaryExpression
from sqlalchemy.orm import Session

from app.database.models.user import User


def find_user(
    session: Session, criteria: Iterable[BinaryExpression] = tuple()
) -> User | None:
    """
    Find a user in the database based on the specified criteria.

    Args:
        :session (Session): The SQLAlchemy database session.
        :criteria (Iterable[BinaryExpression], optional): Criteria to filter users.
            Defaults to an empty tuple.

    Returns:
        :User | None: The user matching the criteria, if found; None, otherwise.
    """
    return session.query(User).filter(*criteria).one_or_none()


def find_users(session: Session, offset: int = 0, limit: int = 100) -> List[User]:
    """
    Retrieve a list of users from the database with optional pagination.

    Args:
        :session (Session): The SQLAlchemy database session.
        :offset (int, optional): The offset index for pagination. Defaults to 0.
        :limit (int, optional): The maximum number of users to retrieve. Defaults to 100.

    Returns:
        :List[User]: A list containing users retrieved from the database according to the specified offset and limit.
    """
    return session.query(User).offset(offset=offset).limit(limit=limit).all()


def add_user(session: Session, user: User) -> None:
    """
    Add a new user to the database session.

    Args:
        :session (Session): The SQLAlchemy database session.
        :user (User): The user object to add to the session.

    Returns:
        None
    """
    session.add(instance=user)
    session.flush()


def delete_user(session: Session, user: User) -> None:
    """
    Delete a user from the database.

    Args:
        :session (Session): The SQLAlchemy database session.
        :user (User): The user object to be deleted.

    Returns:
        None
    """
    session.delete(instance=user)
    session.flush()


def update_user(session: Session, user: User) -> None:
    """
    Update an existing user in the database.

    Args:
        :session (Session): The SQLAlchemy database session.
        :user (User): The user object to be updated.

    Returns:
        None
    """
    add_user(session=session, user=user)
