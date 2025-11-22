from sqlalchemy import create_engine, text
from database import SQLALCHEMY_DATABASE_URL
from models import Base
import os

try:
    print(f"Connecting to: {SQLALCHEMY_DATABASE_URL}")
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    print("Testing connection...")
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print(f"Connection successful: {result.fetchone()}")

    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

except Exception as e:
    print(f"ERROR: {e}")
