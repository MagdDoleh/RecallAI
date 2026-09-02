from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.models import Flashcard, QuizQuestion, Topic, current_time
from backend.repositories import topics as topic_repository
from backend.schemas import (
    SavedStudyMaterialResponse,
    SavedTopicListItem,
    StudyMaterialResponse,
)


class TopicSaveError(Exception):
    pass


class TopicNotFoundError(Exception):
    pass


class TopicUpdateError(Exception):
    pass


class TopicDeleteError(Exception):
    pass


def save_study_material(
    database: Session,
    user_id: int,
    material: StudyMaterialResponse,
) -> SavedStudyMaterialResponse:
    topic = Topic(
        user_id=user_id,
        title=material.topic,
        summary=material.summary,
        key_concepts=[concept.model_dump() for concept in material.key_concepts],
        flashcards=[
            Flashcard(question=flashcard.question, answer=flashcard.answer)
            for flashcard in material.flashcards
        ],
        quiz_questions=[
            QuizQuestion(
                question=question.question,
                answer=question.answer,
                difficulty=question.difficulty,
            )
            for question in material.quiz_questions
        ],
    )

    try:
        saved_topic = topic_repository.save_topic(database, topic)
    except SQLAlchemyError as error:
        raise TopicSaveError from error

    return build_saved_material_response(saved_topic)


def list_saved_topics(
    database: Session,
    user_id: int,
    search: str | None = None,
) -> list[SavedTopicListItem]:
    normalized_search = search.strip() if search else None
    topics = topic_repository.list_topics_for_user(
        database,
        user_id,
        normalized_search,
    )
    return [
        SavedTopicListItem(
            id=topic.id,
            title=topic.title,
            created_at=topic.created_at,
            updated_at=topic.updated_at,
        )
        for topic in topics
    ]


def get_saved_study_material(
    database: Session,
    topic_id: int,
    user_id: int,
) -> SavedStudyMaterialResponse:
    topic = topic_repository.get_topic_for_user(database, topic_id, user_id)
    if topic is None:
        raise TopicNotFoundError
    return build_saved_material_response(topic)


def update_saved_study_material(
    database: Session,
    topic_id: int,
    user_id: int,
    material: StudyMaterialResponse,
) -> SavedStudyMaterialResponse:
    topic = topic_repository.get_topic_for_user(database, topic_id, user_id)
    if topic is None:
        raise TopicNotFoundError

    topic.title = material.topic
    topic.summary = material.summary
    topic.key_concepts = [concept.model_dump() for concept in material.key_concepts]
    topic.updated_at = current_time()
    topic.flashcards = [
        Flashcard(question=flashcard.question, answer=flashcard.answer)
        for flashcard in material.flashcards
    ]
    topic.quiz_questions = [
        QuizQuestion(
            question=question.question,
            answer=question.answer,
            difficulty=question.difficulty,
        )
        for question in material.quiz_questions
    ]

    try:
        updated_topic = topic_repository.update_topic(database, topic)
    except SQLAlchemyError as error:
        raise TopicUpdateError from error
    return build_saved_material_response(updated_topic)


def delete_saved_study_material(
    database: Session,
    topic_id: int,
    user_id: int,
) -> None:
    topic = topic_repository.get_topic_for_user(database, topic_id, user_id)
    if topic is None:
        raise TopicNotFoundError

    try:
        topic_repository.delete_topic(database, topic)
    except SQLAlchemyError as error:
        raise TopicDeleteError from error


def build_saved_material_response(topic: Topic) -> SavedStudyMaterialResponse:
    return SavedStudyMaterialResponse(
        id=topic.id,
        topic=topic.title,
        summary=topic.summary,
        key_concepts=topic.key_concepts,
        flashcards=[
            {"question": card.question, "answer": card.answer}
            for card in sorted(topic.flashcards, key=lambda card: card.id)
        ],
        quiz_questions=[
            {
                "question": question.question,
                "answer": question.answer,
                "difficulty": question.difficulty,
            }
            for question in sorted(topic.quiz_questions, key=lambda question: question.id)
        ],
        created_at=topic.created_at,
        updated_at=topic.updated_at,
    )
