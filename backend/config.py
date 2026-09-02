import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")


JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("RECALLAI_JWT_EXPIRE_MINUTES", "60"))
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")


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
