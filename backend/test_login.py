"""
Test script to verify user exists in database and password verification works
"""
from database import get_db
from models import User
from auth import verify_password
from dotenv import load_dotenv

load_dotenv()

# Get database session
db = next(get_db())

# Check if user exists
user = db.query(User).filter(User.email == "kiranjugdar@yahoo.com").first()

if user:
    print(f"✓ User found: {user.email}")
    print(f"  User ID: {user.id}")
    print(f"  Hashed password: {user.hashed_password[:50]}...")

    # Test password verification
    test_password = "login123"
    is_valid = verify_password(test_password, user.hashed_password)
    print(f"\n  Password verification for 'login123': {'✓ VALID' if is_valid else '✗ INVALID'}")
else:
    print("✗ User not found in database!")
    print("\nAll users in database:")
    all_users = db.query(User).all()
    for u in all_users:
        print(f"  - {u.email}")
