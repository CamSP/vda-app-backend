from fastapi import FastAPI
from app.routers import locations
from app.config import settings
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description=''
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(locations.router, prefix="/api/locations", tags=["locations"])

@app.get("/")
def root():
    return {"status": "ok"}