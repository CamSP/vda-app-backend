from fastapi import APIRouter, HTTPException, Header, Request, Depends
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.database import get_db
from app.schemas.location import NearbyRequest, NearbyResponse
from app.services.geocoding import geocode_address
from app.services.knn import knn_search
from app.config import settings

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.post("/nearby", response_model=NearbyResponse)
@limiter.limit("5/minute")
async def get_nearby_locations(
    request: Request,
    body: NearbyRequest,
    db: Session = Depends(get_db)
):
    try:
        lat, lng = await geocode_address(body.address)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception:
        raise HTTPException(status_code=502, detail="Error al consultar Google Maps.")

    vecinos = knn_search(lat, lng, k=body.k, db=db)

    return NearbyResponse(
        address=body.address,
        lat=0,
        lng=0,
        neighbors=vecinos,
    )