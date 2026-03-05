from fastapi import FastAPI, Depends
from app.routers import locations, daily_verse, notifications
from app.config import settings
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

scheduler.start()


@app.get("/")
def root():
    return {"status": "ok"}