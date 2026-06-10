import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

#  POSTGRES URL z Renderu (alebo .env)
DATABASE_URL = os.getenv("DATABASE_URL")

# fallback pre lokál (ak chceš ešte dev)
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./app.db"

# SQLite needs special args
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()