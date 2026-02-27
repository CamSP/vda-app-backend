import csv
import math
from pathlib import Path
from app.models.location import Location
from app.schemas.location import LocationResult

DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "locations.csv"


def _load_locations() -> list[Location]:
    """Carga los puntos desde el CSV."""
    locations = []
    with open(DATA_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            locations.append(Location(
                id=int(row["id"]),
                name=row["name"],
                lat=float(row["lat"]),
                lng=float(row["lng"]),
                address=row["address"],
                contact=row["contact"]
            ))
    return locations


def _haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Distancia en km entre dos coordenadas usando la fórmula de Haversine."""
    R = 6371  # radio de la Tierra en km
    d_lat = math.radians(lat2 - lat1)
    d_lng = math.radians(lng2 - lng1)
    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(d_lng / 2) ** 2
    )
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def knn_search(lat: float, lng: float, k: int) -> list[LocationResult]:
    """
    Ejecuta KNN manual sobre el CSV y devuelve los k vecinos más cercanos
    ordenados por distancia ascendente.
    """
    locations = _load_locations()

    results = []
    for loc in locations:
        dist = _haversine(lat, lng, loc.lat, loc.lng)
        results.append(LocationResult(
            id=loc.id,
            name=loc.name,
            lat=loc.lat,
            lng=loc.lng,
            address=loc.address,
            contact=str(dist),
            distance=dist
        ))

    results.sort(key=lambda x: x.distance)
    return results[:k]
