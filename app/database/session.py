from typing import Any, Generator

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, declarative_base, sessionmaker

from app.settings import settings

# Create session
engine: Engine = create_engine(url=settings.DB_URI, echo=True)
SessionLocal: sessionmaker = sessionmaker(autocommit=False, autoflush=True, bind=engine)
Base: DeclarativeBase = declarative_base()


def get_db() -> Generator[Any | Session, Any, None]:
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
