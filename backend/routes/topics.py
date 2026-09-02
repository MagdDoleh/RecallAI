from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_database_session
from backend.models import User
from backend.routes.auth import get_current_user
from backend.schemas import (
    SavedStudyMaterialResponse,
    SavedTopicListItem,
    StudyMaterialResponse,
)
from backend.services import topics as topic_service


router = APIRouter(prefix="/topics", tags=["saved study guides"])

DatabaseSession = Annotated[Session, Depends(get_database_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post(
    "",
    response_model=SavedStudyMaterialResponse,
    status_code=status.HTTP_201_CREATED,
)
def save_topic(
    material: StudyMaterialResponse,
    database: DatabaseSession,
    current_user: CurrentUser,
) -> SavedStudyMaterialResponse:
    try:
        return topic_service.save_study_material(database, current_user.id, material)
    except topic_service.TopicSaveError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The study guide could not be saved. Please try again.",
        ) from error


@router.get("", response_model=list[SavedTopicListItem])
def list_topics(
    database: DatabaseSession,
    current_user: CurrentUser,
) -> list[SavedTopicListItem]:
    return topic_service.list_saved_topics(database, current_user.id)


@router.get("/{topic_id}", response_model=SavedStudyMaterialResponse)
def read_topic(
    topic_id: int,
    database: DatabaseSession,
    current_user: CurrentUser,
) -> SavedStudyMaterialResponse:
    try:
        return topic_service.get_saved_study_material(
            database,
            topic_id,
            current_user.id,
        )
    except topic_service.TopicNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved study guide not found.",
        ) from error
