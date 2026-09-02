from google import genai
from google.genai import types
from pydantic import ValidationError

from backend.config import GEMINI_MODEL, get_gemini_api_key
from backend.schemas import GeneratedStudyContent, StudyMaterialResponse


SYSTEM_INSTRUCTION = """
You are RecallAI's study-material generator. Create accurate, concise, beginner-friendly
material that helps a learner understand and review the requested topic. Define unfamiliar
terms, avoid unnecessary jargon, and do not invent facts. Produce a useful summary, five
key concepts, five flashcards, and five quiz questions. Spread quiz difficulty across easy,
medium, and hard when the topic allows it.
""".strip()


class GeminiNotConfiguredError(Exception):
    pass


class GeminiGenerationError(Exception):
    pass


class GeminiResponseError(Exception):
    pass


def generate_study_material(topic: str) -> StudyMaterialResponse:
    try:
        api_key = get_gemini_api_key()
    except RuntimeError as error:
        raise GeminiNotConfiguredError from error

    try:
        with genai.Client(api_key=api_key) as client:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=f'Create study material for the topic: "{topic}".',
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    response_mime_type="application/json",
                    response_schema=GeneratedStudyContent,
                    temperature=0.3,
                ),
            )
    except Exception as error:
        raise GeminiGenerationError from error

    try:
        if response.parsed is not None:
            content = GeneratedStudyContent.model_validate(response.parsed)
        elif response.text:
            content = GeneratedStudyContent.model_validate_json(response.text)
        else:
            raise GeminiResponseError
    except (ValidationError, ValueError, TypeError) as error:
        raise GeminiResponseError from error

    return StudyMaterialResponse(topic=topic, **content.model_dump())
