from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.models import Flashcard, QuizQuestion, Topic
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


def list_saved_topics(database: Session, user_id: int) -> list[SavedTopicListItem]:
    topics = topic_repository.list_topics_for_user(database, user_id)
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
