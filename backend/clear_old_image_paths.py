"""
Clear old file paths from image_path column (replace with NULL)
This is needed after migrating from file-based to URL-based caching
"""
from database import get_db
from models import Word
from dotenv import load_dotenv

load_dotenv()

db = next(get_db())

# Find all words with image_path that are file paths (not URLs)
words_with_old_paths = db.query(Word).filter(
    Word.image_path.isnot(None),
    ~Word.image_path.startswith('http')
).all()

print(f"Found {len(words_with_old_paths)} words with old file paths")

for word in words_with_old_paths:
    print(f"  Clearing: {word.jp_word} - {word.image_path}")
    word.image_path = None

db.commit()
print(f"✅ Cleared {len(words_with_old_paths)} old file paths")
