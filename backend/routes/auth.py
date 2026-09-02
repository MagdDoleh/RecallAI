from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from backend.database import get_database_session
from backend.models import User
from backend.repositories import users as user_repository
from backend.schemas import TokenResponse, UserLogin, UserRegistration, UserResponse
from backend.services import auth as auth_service


router = APIRouter(prefix="/auth", tags=["authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

DatabaseSession = Annotated[Session, Depends(get_database_session)]
AccessToken = Annotated[str, Depends(oauth2_scheme)]


def get_current_user(database: DatabaseSession, token: AccessToken) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate authentication credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        user_id = auth_service.get_user_id_from_token(token)
    except auth_service.InvalidAccessTokenError as error:
        raise credentials_error from error

    user = user_repository.get_user_by_id(database, user_id)
    if user is None:
        raise credentials_error
    return user


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(registration: UserRegistration, database: DatabaseSession) -> User:
    try:
        return auth_service.register_user(database, registration)
    except auth_service.UsernameAlreadyExistsError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="That username is already registered.",
        ) from error
    except auth_service.EmailAlreadyExistsError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="That email address is already registered.",
        ) from error


@router.post("/login", response_model=TokenResponse)
def login(login_data: UserLogin, database: DatabaseSession) -> TokenResponse:
    try:
        user = auth_service.authenticate_user(
            database,
            identifier=login_data.identifier,
            password=login_data.password,
        )
    except auth_service.InvalidCredentialsError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username, email, or password.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from error

    return TokenResponse(access_token=auth_service.create_access_token(user.id))


@router.get("/me", response_model=UserResponse)
def read_current_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    return current_user
