from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.calendar_sync import SyncResult
from app.services.calendar_sync import sync_calendar
from app.auth.api_key import verify_api_key

router = APIRouter()


@router.post("/sync", response_model=SyncResult)
def force_sync(
    days: int = Query(default=30, ge=7, le=90, description="Días hacia adelante a sincronizar"),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):
    """
    Fuerza una sincronización inmediata entre Google Calendar y WordPress.
    Requiere API Key.
    """
    result = sync_calendar(db=db, days=days)
    return result