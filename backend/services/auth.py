from datetime import UTC, datetime, timedelta

import jwt
from jwt.exceptions import InvalidTokenError as JWTDecodeError
from pwdlib import PasswordHash
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.config import JWT_ALGORITHM, JWT_EXPIRE_MINUTES, get_jwt_secret
from backend.models import User
from backend.repositories import users as user_repository
from backend.schemas import UserRegistration


password_hash = PasswordHash.recommended()


class UsernameAlreadyExistsError(Exception):
    pass


class EmailAlreadyExistsError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class InvalidAccessTokenError(Exception):
    pass


def register_user(database: Session, registration: UserRegistration) -> User:
    if user_repository.get_user_by_username(database, registration.username):
        raise UsernameAlreadyExistsError

    normalized_email = str(registration.email).lower()
    if user_repository.get_user_by_email(database, normalized_email):
        raise EmailAlreadyExistsError

    hashed_password = password_hash.hash(registration.password)

    try:
        return user_repository.create_user(
            database=database,
            username=registration.username,
            email=normalized_email,
            password_hash=hashed_password,
        )
    except IntegrityError as error:
        if user_repository.get_user_by_email(database, normalized_email):
            raise EmailAlreadyExistsError from error
        raise UsernameAlreadyExistsError from error


def authenticate_user(database: Session, identifier: str, password: str) -> User:
    user = user_repository.get_user_by_identifier(database, identifier)
    if user is None or not password_hash.verify(password, user.password_hash):
        raise InvalidCredentialsError
    return user


def create_access_token(user_id: int) -> str:
    issued_at = datetime.now(UTC)
    payload = {
        "sub": str(user_id),
        "iat": issued_at,
        "exp": issued_at + timedelta(minutes=JWT_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, get_jwt_secret(), algorithm=JWT_ALGORITHM)


def get_user_id_from_token(token: str) -> int:
    try:
        payload = jwt.decode(token, get_jwt_secret(), algorithms=[JWT_ALGORITHM])
        subject = payload.get("sub")
        if subject is None:
            raise InvalidAccessTokenError
        return int(subject)
    except (JWTDecodeError, TypeError, ValueError) as error:
        raise InvalidAccessTokenError from error
