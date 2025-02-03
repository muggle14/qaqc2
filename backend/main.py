# main.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import FastAPI, Depends
from models import Base  # Import your SQLAlchemy models

# Import credentials from config.py
from config import DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT, DATABASE_NAME

# Construct the DATABASE_URL using credentials from config.py
DATABASE_URL = f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"

def ensure_database_exists(db_url: str):
    """
    Ensure that the target database and required schemas exist.
    If they do not, connect to the default database ('postgres')
    and create the target database and schemas.
    """
    from sqlalchemy.engine import url as sa_url
    import psycopg2
    from psycopg2 import sql

    # Parse the connection URL.
    parsed_url = sa_url.make_url(db_url)
    # Use a default database (typically 'postgres') to create the target database if necessary.
    default_db_url = parsed_url.set(database="postgres")

    try:
        # Connect to the default database.
        conn = psycopg2.connect(
            host=default_db_url.host,
            port=default_db_url.port,
            user=default_db_url.username,
            password=default_db_url.password,
            database=default_db_url.database
        )
    except Exception as e:
        raise Exception(f"Failed to connect to the default database: {e}")

    conn.autocommit = True
    cur = conn.cursor()

    # Check if the target database exists.
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (parsed_url.database,))
    exists = cur.fetchone()

    if not exists:
        # Create the target database if it doesn't exist.
        try:
            cur.execute(
                sql.SQL("CREATE DATABASE {}").format(
                    sql.Identifier(parsed_url.database)
                )
            )
            print(f"Database '{parsed_url.database}' created.")
        except Exception as e:
            raise Exception(f"Failed to create database '{parsed_url.database}': {e}")
    else:
        print(f"Database '{parsed_url.database}' already exists.")

    cur.close()
    conn.close()

    # Connect to the target database to create schemas.
    try:
        conn = psycopg2.connect(
            host=parsed_url.host,
            port=parsed_url.port,
            user=parsed_url.username,
            password=parsed_url.password,
            database=parsed_url.database
        )
    except Exception as e:
        raise Exception(f"Failed to connect to the target database: {e}")

    conn.autocommit = True
    cur = conn.cursor()

    # Create the 'auth' schema if it doesn't exist.
    cur.execute("CREATE SCHEMA IF NOT EXISTS auth")
    print("Schema 'auth' ensured.")

    cur.close()
    conn.close()

# Ensure the target database exists before proceeding.
ensure_database_exists(DATABASE_URL)

# Create the SQLAlchemy engine and session.
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables (and views via DDL events in your models) if they don't exist.
Base.metadata.create_all(bind=engine)

# Initialize the FastAPI app.
app = FastAPI(title="Python Backend with PostgreSQL")

# Dependency to get a session per request.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Hello World from the FastAPI backend!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
