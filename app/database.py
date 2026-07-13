# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# ✅ ដាក់ DATABASE_URL ដោយផ្ទាល់ មិនបាច់អានពី .env
DATABASE_URL = "postgresql://neondb_owner:npg_EqDI7gb5BtQV@ep-purple-butterfly-atuzjnrs-pooler.c-9.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()