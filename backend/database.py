import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./taskflow.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def migrate():
    """기존 DB에 누락된 컬럼을 추가한다 — Alembic 없이 SQLite ALTER TABLE 사용"""
    from sqlalchemy import inspect, text
    inspector = inspect(engine)
    try:
        existing = [c["name"] for c in inspector.get_columns("tasks")]
        if "category" not in existing:
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE tasks ADD COLUMN category VARCHAR(100)"))
                conn.commit()
    except Exception:
        pass
