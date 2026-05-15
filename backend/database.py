"""
database.py for the Database Connection
Khaled's file. Handles connecting to PostgreSQL production
or SQLite for quick local testing without installing PostgreSQL
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker



DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./train_system.db")

# Some hosts provide postgres:// URLs, while SQLAlchemy expects postgresql://.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)


connection_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
sql_echo = os.getenv("SQL_ECHO", "false").lower() in {"1", "true", "yes", "on"}


engine = create_engine(
    DATABASE_URL,
    connect_args=connection_args,
    echo=sql_echo,
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
