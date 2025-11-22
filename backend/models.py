from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from database import Base
import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    
    words = relationship("UserWord", back_populates="user")

class Word(Base):
    __tablename__ = "words"

    id = Column(Integer, primary_key=True, index=True)
    jp_word = Column(String, unique=True, index=True)
    reading = Column(String)
    romaji = Column(String)
    english = Column(String)
    image_search_term = Column(String)
    image_path = Column(String, nullable=True)  # Cache generated image path

    user_associations = relationship("UserWord", back_populates="word")

class UserWord(Base):
    __tablename__ = "user_words"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    word_id = Column(Integer, ForeignKey("words.id"))
    status = Column(String, default="new") # new, learning, mastered
    next_review_date = Column(DateTime, default=datetime.datetime.utcnow)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="words")
    word = relationship("Word", back_populates="user_associations")
