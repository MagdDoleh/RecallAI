from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.models import User


def get_user_by_username(database: Session, username: str) -> User | None:
    statement = select(User).where(func.lower(User.username) == username.lower())
    return database.scalar(statement)


def get_user_by_email(database: Session, email: str) -> User | None:
    statement = select(User).where(func.lower(User.email) == email.lower())
    return database.scalar(statement)


def get_user_by_identifier(database: Session, identifier: str) -> User | None:
    normalized_identifier = identifier.lower()
    statement = select(User).where(
        or_(
            func.lower(User.username) == normalized_identifier,
            func.lower(User.email) == normalized_identifier,
        )
    )
    return database.scalar(statement)


def get_user_by_id(database: Session, user_id: int) -> User | None:
    return database.get(User, user_id)


def create_user(
    database: Session,
    username: str,
    email: str,
    password_hash: str,
) -> User:
    user = User(username=username, email=email.lower(), password_hash=password_hash)
    database.add(user)

    try:
        database.commit()
    except IntegrityError:
        database.rollback()
        raise

    database.refresh(user)
    return user
