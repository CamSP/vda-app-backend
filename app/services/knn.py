import math
from sqlalchemy.orm import Session
from app.models.location import Location
from app.schemas.location import LocationResult


def _haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    R = 6371
    d_lat = math.radians(lat2 - lat1)
    d_lng = math.radians(lng2 - lng1)
    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(d_lng / 2) ** 2
    )
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def knn_search(lat: float, lng: float, k: int, db: Session) -> list[LocationResult]:
    locations = db.query(Location).all()
    
    if not locations:
        return []

    results = []
    for loc in locations:
        dist = _haversine(lat, lng, loc.lat, loc.lng)
        results.append(LocationResult(
            id=loc.id,
            name=loc.name,
            address=loc.address,
            lat=loc.lat,
            lng=loc.lng,
            contact=loc.contact,
            distance=round(dist, 3),
        ))

    results.sort(key=lambda x: x.distance)
    return results[:k]