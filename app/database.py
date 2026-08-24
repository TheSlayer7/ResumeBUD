import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./resume_screener.db")
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Path("uploads").mkdir(exist_ok=True)
    Base.metadata.create_all(bind=engine)
    if DATABASE_URL.startswith("sqlite"):
        additions = {
            "candidates": {"projects": "TEXT", "certifications": "TEXT", "ats_score": "REAL", "ats_feedback": "TEXT", "used_ocr": "INTEGER"},
            "jobs": {"company": "TEXT"},
        }
        with engine.begin() as connection:
            for table, columns in additions.items():
                existing = {column["name"] for column in inspect(engine).get_columns(table)}
                for column, column_type in columns.items():
                    if column not in existing:
                        default = "0" if column in {"ats_score", "used_ocr"} else ("'[]'" if column != "company" else "''")
                        connection.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {column_type} NOT NULL DEFAULT {default}"))
            if "used_ocr" in {column["name"] for column in inspect(engine).get_columns("candidates")}:
                connection.execute(text("UPDATE candidates SET used_ocr = 0 WHERE CAST(used_ocr AS TEXT) NOT IN ('0', '1')"))
    from .models import Candidate
    from .services.ats_analyzer import analyze_ats
    from .services.resume_parser import parse_resume

    with SessionLocal() as db:
        candidates = db.query(Candidate).all()
        for candidate in candidates:
            parsed = parse_resume(candidate.raw_text or "")
            candidate.ats_score, candidate.ats_feedback = analyze_ats(
                candidate.raw_text or "", parsed, used_ocr=bool(candidate.used_ocr)
            )
        if candidates:
            db.commit()
