#!/usr/bin/env python3
"""SQLAlchemy database setup for the application."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session


# Prefer absolute path for the SQLite DB file
DATABASE_URL = "sqlite:////workspace/app.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    future=True,
)

SessionLocal = scoped_session(
    sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)
)

Base = declarative_base()

