from collections.abc import Generator
import os

from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from backend.config import PROJECT_ROOT

DATABASE_PATH = PROJECT_ROOT / "recallai.db"
LOCAL_DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"


def get_database_url() -> str:
    database_url = os.getenv("DATABASE_URL", LOCAL_DATABASE_URL)
    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql+psycopg://", 1)
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return database_url


DATABASE_URL = get_database_url()
engine_options = {}
if DATABASE_URL.startswith("sqlite"):
    engine_options["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **engine_options)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


if engine.dialect.name == "sqlite":
    @event.listens_for(engine, "connect")
    def enable_sqlite_foreign_keys(dbapi_connection, connection_record) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def create_database_tables() -> None:
    # Importing the models registers their tables with Base before creation.
    from backend import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    ensure_topic_key_concepts_column()


def ensure_topic_key_concepts_column() -> None:
    if engine.dialect.name != "sqlite":
        return

    topic_columns = {
        column["name"] for column in inspect(engine).get_columns("topics")
    }
    if "key_concepts" in topic_columns:
        return

    with engine.begin() as connection:
        connection.execute(
            text(
                "ALTER TABLE topics "
                "ADD COLUMN key_concepts JSON NOT NULL DEFAULT '[]'"
            )
        )


def get_database_session() -> Generator[Session, None, None]:
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()
