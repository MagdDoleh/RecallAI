from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import create_database_tables
from backend.routes.auth import router as auth_router
from backend.routes.generation import router as generation_router


app = FastAPI(title="RecallAI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

create_database_tables()
app.include_router(auth_router)
app.include_router(generation_router)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "RecallAI API is running"}
