import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()
url = os.getenv("DATABASE_URL", "sqlite:///./dev.db")
if url.startswith("postgresql://"):
    url = url.replace("postgresql://", "postgresql+psycopg://", 1)
engine = create_engine(
    url, connect_args={"check_same_thread": False} if url.startswith("sqlite") else {}
)
SessionLocal = sessionmaker(engine)


@event.listens_for(engine, "connect")
def enable_sqlite_foreign_keys(connection, _record):
    if engine.dialect.name == "sqlite":
        connection.execute("PRAGMA foreign_keys=ON")


class Base(DeclarativeBase):
    pass


def get_db():
    with SessionLocal() as session:
        yield session
