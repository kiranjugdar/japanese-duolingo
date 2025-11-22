"""
Run this script to create all database tables in Supabase
Usage: python create_tables.py
"""
from database import engine, Base
from models import User, Word, UserWord
from dotenv import load_dotenv

load_dotenv()

print("Creating database tables...")
try:
    Base.metadata.create_all(bind=engine)
    print("✅ All tables created successfully!")
    print("\nTables created:")
    print("  - users")
    print("  - words")
    print("  - user_words")
except Exception as e:
    print(f"❌ Error creating tables: {e}")
    import traceback
    traceback.print_exc()
