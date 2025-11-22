from fastapi import FastAPI, HTTPException, Depends, Response
from fastapi.responses import FileResponse
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
import httpx
import time
import logging

logger = logging.getLogger("uvicorn")

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


class ImageGenerateRequest(BaseModel):
    word: str
    english_meaning: str


async def fetch_image_from_pexels(search_term: str) -> str:
    """
    Fetch image URL from Pexels API (fast, free stock photos)
    Returns the image URL if found, None otherwise
    """
    pexels_api_key = os.getenv("PEXELS_API_KEY")
    if not pexels_api_key:
        logger.warning("PEXELS_API_KEY not set in .env file")
        return None

    try:
        headers = {"Authorization": pexels_api_key}
        url = f"https://api.pexels.com/v1/search?query={search_term}&per_page=1&orientation=square"

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            if data.get("photos") and len(data["photos"]) > 0:
                # Get medium-sized image (faster download)
                image_url = data["photos"][0]["src"]["medium"]
                logger.info(f"✓ Found Pexels image for '{search_term}'")
                return image_url
            else:
                logger.info(f"✗ No Pexels image found for '{search_term}'")
                return None
    except Exception as e:
        logger.warning(f"Pexels API error for '{search_term}': {e}")
        return None


async def generate_image_with_pollinations(search_term: str) -> str:
    """
    Generate image using Pollinations.ai (fallback)
    Returns the image URL
    """
    prompt = f"a simple clear photo of {search_term}"
    image_url = f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '%20')}?width=512&height=512&nologo=true"
    logger.info(f"🎨 Generating image with Pollinations.ai for '{search_term}'")
    return image_url


@app.post("/generate-image")
async def generate_word_image(
    request: ImageGenerateRequest,
    current_user: User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get image for a Japanese word:
    1. Check cache (database)
    2. Try Pexels API (fast, free stock photos)
    3. Fallback to Pollinations.ai (AI generation)
    """
    try:
        start_time = time.time()

        # Check if we already have a cached image for this word
        db_word = db.query(Word).filter(Word.jp_word == request.word).first()

        # Create output directory if it doesn't exist
        output_dir = os.path.join(os.path.dirname(__file__), "generated_images")
        os.makedirs(output_dir, exist_ok=True)

        if db_word and db_word.image_path and os.path.exists(db_word.image_path):
            # Return cached image
            elapsed_time = time.time() - start_time
            logger.info(f"⚡ CACHE HIT: Returning cached image for {request.word} (took {elapsed_time:.2f}s)")
            return FileResponse(
                db_word.image_path,
                media_type="image/png",
                filename=f"{request.word}_{request.english_meaning}.png"
            )

        logger.info(f"🔍 Fetching new image for {request.word} ({request.english_meaning})")

        # Try Pexels API first (fast stock photos)
        image_url = await fetch_image_from_pexels(request.english_meaning)
        source = "Pexels"

        # Fallback to AI generation if no stock photo found
        if not image_url:
            image_url = await generate_image_with_pollinations(request.english_meaning)
            source = "Pollinations.ai"

        # Download the image
        fetch_start = time.time()
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(image_url)
            response.raise_for_status()

            # Save image locally
            safe_filename = f"{request.word}_{request.english_meaning.replace(' ', '_')}.png"
            image_path = os.path.join(output_dir, safe_filename)

            with open(image_path, "wb") as f:
                f.write(response.content)

        fetch_time = time.time() - fetch_start
        total_time = time.time() - start_time
        logger.info(f"✅ Image from {source} saved in {fetch_time:.2f}s, total time: {total_time:.2f}s")

        # Cache the image path in database
        if db_word:
            db_word.image_path = image_path
            db.commit()

        return FileResponse(
            image_path,
            media_type="image/png",
            filename=f"{request.word}_{request.english_meaning}.png"
        )
    except Exception as e:
        logger.error(f"Error getting image: {e}")
        raise HTTPException(status_code=500, detail=str(e))
