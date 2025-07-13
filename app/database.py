import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Load environment variables from .env file
load_dotenv()

# Read database connection info from environment variables
MYSQL_USER = os.getenv("DATABASE_USER")
MYSQL_PASSWORD = os.getenv("DATABASE_PASSWORD")
MYSQL_DB = os.getenv("DATABASE_NAME")
MYSQL_HOST = os.getenv("DATABASE_HOST", "localhost")
MYSQL_PORT = os.getenv("DATABASE_PORT", "3306")  # as string for f-string

# Construct the full database URL
DATABASE_URL = (
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
)

# Create the SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,   # Helps to check if connection is alive before using it
)

# Create a configured "Session" class
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for our ORM models
Base = declarative_base()

# Dependency to get DB session, use in FastAPI routes
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
