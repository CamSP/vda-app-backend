from sqlalchemy.orm import Session
from app.models.daily_verse import DailyVerse
from app.schemas.verse import DailyVerseResponse
from datetime import date
from app.services.notifications import broadcast

def get_today_verse(db: Session) -> DailyVerseResponse | None:
    today = date.today()
    return db.query(DailyVerse).filter(DailyVerse.date == today).first()

def notify_daily_verse(db: Session):
    verse = get_today_verse(db)
    if not verse:
        print("No hay versículo para hoy, no se envió notificación.")
        return
    broadcast(title="Versículo del día 📖", body=verse.verse, db=db)
