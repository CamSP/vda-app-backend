from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.verse import VerseResponse, DailyVerseResponse
from app.services.getDailyVerse import get_today_verse

router = APIRouter()

@router.get("/daily", response_model=DailyVerseResponse)
def today_verse(db: Session = Depends(get_db)):
    verse = get_today_verse(db)

    if not verse:
        raise HTTPException(status_code=404, detail="No hay versículo para hoy")
    return verse
