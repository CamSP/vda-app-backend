from fastapi import APIRouter, HTTPException, Request
from app.schemas.location import NearbyRequest, NearbyResponse
from app.services.geocoding import geocode_address
from app.services.knn import knn_search

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

router = APIRouter()

@router.post("/nearby", response_model=NearbyResponse)
@limiter.limit("2/minute") 
async def get_nearby_locations(body: NearbyRequest, request: Request):
    """
    Recibe una dirección en Bogotá, la geocodifica con Google Maps
    y devuelve los k puntos más cercanos usando KNN.
    """
    # 1. Geocodificar la dirección
    try:
        lat, lng = await geocode_address(body.address)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception:
        raise HTTPException(status_code=502, detail="Error al consultar la API de Google Maps.")

    # 2. Ejecutar KNN
    vecinos = knn_search(lat, lng, k=body.k)

    return NearbyResponse(
        address=body.address,
        lat=lat,
        lng=lng,
        neighbors=vecinos,
    )
