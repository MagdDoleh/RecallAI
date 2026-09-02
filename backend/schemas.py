from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserRegistration(BaseModel):
    username: str = Field(min_length=3, max_length=50, pattern=r"^[A-Za-z0-9_]+$")
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator("username", mode="before")
    @classmethod
    def strip_username(cls, value: str) -> str:
        return value.strip() if isinstance(value, str) else value


class UserLogin(BaseModel):
    identifier: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=1, max_length=128)

    @field_validator("identifier", mode="before")
    @classmethod
    def strip_identifier(cls, value: str) -> str:
        return value.strip() if isinstance(value, str) else value


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class StudyGenerationRequest(BaseModel):
    topic: str = Field(min_length=3, max_length=200)

    @field_validator("topic", mode="before")
    @classmethod
    def strip_topic(cls, value: str) -> str:
        return value.strip() if isinstance(value, str) else value

    @field_validator("topic")
    @classmethod
    def require_readable_topic(cls, value: str) -> str:
        if not any(character.isalnum() for character in value):
            raise ValueError("Topic must include at least one letter or number.")
        return value


class KeyConcept(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    explanation: str = Field(min_length=1, max_length=1000)


class GeneratedFlashcard(BaseModel):
    question: str = Field(min_length=1, max_length=500)
    answer: str = Field(min_length=1, max_length=1000)


class GeneratedQuizQuestion(BaseModel):
    question: str = Field(min_length=1, max_length=500)
    answer: str = Field(min_length=1, max_length=1000)
    difficulty: Literal["easy", "medium", "hard"]


class GeneratedStudyContent(BaseModel):
    summary: str = Field(min_length=1, max_length=5000)
    key_concepts: list[KeyConcept] = Field(min_length=3, max_length=8)
    flashcards: list[GeneratedFlashcard] = Field(min_length=3, max_length=8)
    quiz_questions: list[GeneratedQuizQuestion] = Field(min_length=3, max_length=8)


class StudyMaterialResponse(GeneratedStudyContent):
    topic: str


class SavedTopicListItem(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime


class SavedStudyMaterialResponse(BaseModel):
    id: int
    topic: str
    summary: str
    key_concepts: list[KeyConcept]
    flashcards: list[GeneratedFlashcard]
    quiz_questions: list[GeneratedQuizQuestion]
    created_at: datetime
    updated_at: datetime
