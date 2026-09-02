from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.config import get_cors_origins
from backend.database import create_database_tables
from backend.routes.auth import router as auth_router
from backend.routes.generation import router as generation_router
from backend.routes.topics import router as topics_router


app = FastAPI(title="RecallAI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

create_database_tables()
app.include_router(auth_router)
app.include_router(generation_router)
app.include_router(topics_router)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "RecallAI API is running"}


FRONTEND_DIRECTORY = Path(__file__).resolve().parent.parent / "frontend"


@app.get("/app", include_in_schema=False)
def serve_frontend() -> FileResponse:
    return FileResponse(FRONTEND_DIRECTORY / "index.html")


app.mount("/css", StaticFiles(directory=FRONTEND_DIRECTORY / "css"), name="frontend-css")
app.mount("/js", StaticFiles(directory=FRONTEND_DIRECTORY / "js"), name="frontend-js")
