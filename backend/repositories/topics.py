from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from backend.models import Topic


def save_topic(database: Session, topic: Topic) -> Topic:
    database.add(topic)
    try:
        database.commit()
    except SQLAlchemyError:
        database.rollback()
        raise

    saved_topic = get_topic_for_user(database, topic.id, topic.user_id)
    if saved_topic is None:
        raise SQLAlchemyError("The saved topic could not be reloaded.")
    return saved_topic


def list_topics_for_user(database: Session, user_id: int) -> list[Topic]:
    statement = (
        select(Topic)
        .where(Topic.user_id == user_id)
        .order_by(Topic.updated_at.desc(), Topic.id.desc())
    )
    return list(database.scalars(statement))


def get_topic_for_user(database: Session, topic_id: int, user_id: int) -> Topic | None:
    statement = (
        select(Topic)
        .where(Topic.id == topic_id, Topic.user_id == user_id)
        .options(
            selectinload(Topic.flashcards),
            selectinload(Topic.quiz_questions),
        )
    )
    return database.scalar(statement)
