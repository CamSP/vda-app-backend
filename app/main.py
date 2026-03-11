from fastapi import FastAPI, Depends
from app.routers import locations, daily_verse, notifications, calendar_sync
from app.config import settings
from app.services.calendar_sync import sync_calendar
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.database import SessionLocal
import logging

logger = logging.getLogger(__name__)

from app.services.getDailyVerse import notify_daily_verse

scheduler = AsyncIOScheduler()

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description='',
    
)

# Limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Routes
app.include_router(locations.router, prefix="/locations", tags=["locations"])
app.include_router(daily_verse.router, prefix="/verse", tags=["verse"])
app.include_router(
    notifications.router,
    prefix="/notifications",
    tags=["notifications"]
)
app.include_router(calendar_sync.router, prefix="/calendar", tags=["calendar"])

# Crons
@scheduler.scheduled_job("cron", hour=6, minute=0)  # todos los días a las 8am
def daily_verse_job():
    db = SessionLocal()
    try:
        notify_daily_verse(db)
    except Exception as e:
        logger.error(f"Error en daily_verse_job: {e}")
    finally:
        db.close()

@scheduler.scheduled_job("cron", hour=0, minute=0) # todos los días a las 2am
def calendar_sync_job():
    db = SessionLocal()
    try:
        sync_calendar(db=db, days=60)
    except Exception as e:
        logger.error(f"Error en calendar_sync_job: {e}")
    finally:
        db.close()

scheduler.start()


@app.get("/")
def root():
    return {"status": "ok"}