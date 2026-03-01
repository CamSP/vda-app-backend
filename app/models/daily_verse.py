from sqlalchemy import Column, Integer, String, Date
from app.database import Base

class DailyVerse(Base):
    __tablename__ = "daily_verse"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date)
    summary = Column(String(500))
    verse = Column(String(100))
    verse_text = Column(String(500))