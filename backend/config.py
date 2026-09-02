import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")


JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("RECALLAI_JWT_EXPIRE_MINUTES", "60"))
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
LOCAL_CORS_ORIGINS = ["http://127.0.0.1:5500", "http://localhost:5500"]


def get_cors_origins() -> list[str]:
    configured_origins = os.getenv("RECALLAI_CORS_ORIGINS")
    if configured_origins is None:
        return LOCAL_CORS_ORIGINS
    return [origin.strip().rstrip("/") for origin in configured_origins.split(",") if origin.strip()]


def get_jwt_secret() -> str:
    secret = os.getenv("RECALLAI_JWT_SECRET")
    if not secret or len(secret) < 32:
        raise RuntimeError(
            "RECALLAI_JWT_SECRET must be set to a value at least 32 characters long."
        )
    return secret


def get_gemini_api_key() -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")
    return api_key
