from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import json

load_dotenv()

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class GenerateRequest(BaseModel):
    excluded_words: List[str] = []

class Word(BaseModel):
    jp_word: str
    reading: str
    romaji: str
    english: str
    image_search_term: str

class GenerateResponse(BaseModel):
    words: List[Word]

@app.post("/generate", response_model=GenerateResponse)
async def generate_words(request: GenerateRequest):
    try:
        prompt = f"""
        Generate 3 beginner Japanese words that are NOT in this list: {request.excluded_words}.
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
        return data

    except Exception as e:
        print(f"Error generating words: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"message": "Japanese Learning API is running"}
