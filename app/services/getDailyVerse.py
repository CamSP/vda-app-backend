from sqlalchemy.orm import Session
from app.models.daily_verse import DailyVerse
from app.schemas.verse import DailyVerseResponse
from datetime import date

def get_today_verse(db: Session) -> DailyVerseResponse | None:
    today = date.today()
    return db.query(DailyVerse).filter(DailyVerse.date == today).first()
