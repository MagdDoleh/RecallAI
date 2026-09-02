from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from backend.models import User
from backend.routes.auth import get_current_user
from backend.schemas import StudyGenerationRequest, StudyMaterialResponse
from backend.services import gemini


router = APIRouter(tags=["study generation"])


@router.post("/generate", response_model=StudyMaterialResponse)
def generate(
    request: StudyGenerationRequest,
    current_user: Annotated[User, Depends(get_current_user)],
) -> StudyMaterialResponse:
    try:
        return gemini.generate_study_material(request.topic)
    except gemini.GeminiNotConfiguredError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Study generation is not configured. Set GEMINI_API_KEY on the backend.",
        ) from error
    except gemini.GeminiResponseError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Gemini returned study material in an unexpected format. Please try again.",
        ) from error
    except gemini.GeminiGenerationError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Gemini could not generate study material. Check the API key and try again.",
        ) from error
