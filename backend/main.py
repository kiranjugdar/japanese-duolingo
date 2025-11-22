from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import json
from sqlalchemy.orm import Session
from database import engine, get_db, Base
from models import User, Word, UserWord
import auth

load_dotenv()

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class GenerateRequest(BaseModel):
    pass # No longer need excluded_words from client

class WordResponse(BaseModel):
    jp_word: str
    reading: str
    romaji: str
    english: str
    image_search_term: str

class GenerateResponse(BaseModel):
    words: List[WordResponse]

@app.post("/generate", response_model=GenerateResponse)
async def generate_words(
    request: GenerateRequest, 
    current_user: User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Get words the user already has
        user_words = db.query(UserWord).filter(UserWord.user_id == current_user.id).all()
        excluded_word_ids = [uw.word_id for uw in user_words]
        
        # Get actual word strings to exclude
        existing_words = db.query(Word).filter(Word.id.in_(excluded_word_ids)).all()
        excluded_words_list = [w.jp_word for w in existing_words]

        prompt = f"""
        Generate 3 beginner Japanese words that are NOT in this list: {excluded_words_list}.
        For each word, provide:
        - jp_word: The word in Japanese (Kanji/Kana)
        - reading: The reading in Hiragana/Katakana
        - romaji: The reading in Romaji
        - english: The English meaning
        - image_search_term: A simple English search term to find an image for this word (e.g. "apple" for "ringo")
        
        Return ONLY a JSON object with a key "words" containing the list of objects.
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful Japanese language teacher. Output valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content
        data = json.loads(content)
        
        new_words_data = data.get("words", [])
        response_words = []

        for w_data in new_words_data:
            # Check if word exists in global DB, if not create it
            db_word = db.query(Word).filter(Word.jp_word == w_data["jp_word"]).first()
            if not db_word:
                db_word = Word(
                    jp_word=w_data["jp_word"],
                    reading=w_data["reading"],
                    romaji=w_data["romaji"],
                    english=w_data["english"],
                    image_search_term=w_data["image_search_term"]
                )
                db.add(db_word)
                db.commit()
                db.refresh(db_word)
            
            # Link to user
            user_word = UserWord(user_id=current_user.id, word_id=db_word.id)
            db.add(user_word)
            db.commit()
            
            response_words.append(w_data)

        return {"words": response_words}

    except Exception as e:
        print(f"Error generating words: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"message": "Japanese Learning API is running"}
