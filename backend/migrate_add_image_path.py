"""
Migration script to add image_path column to words table
Run this once to update existing database
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

def migrate():
    SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
    if not SQLALCHEMY_DATABASE_URL:
        print("Error: DATABASE_URL not found in environment")
        return

    engine = create_engine(SQLALCHEMY_DATABASE_URL)

    with engine.connect() as conn:
        # Check if column already exists (PostgreSQL)
        result = conn.execute(text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name='words' AND column_name='image_path'
        """))
        exists = result.fetchone() is not None

        if not exists:
            print("Adding image_path column to words table...")
            conn.execute(text("ALTER TABLE words ADD COLUMN image_path VARCHAR"))
            conn.commit()
            print("Migration completed successfully!")
        else:
            print("image_path column already exists, skipping migration")

if __name__ == "__main__":
    migrate()
