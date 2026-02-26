from pydantic import BaseModel


class NearbyRequest(BaseModel):
    address: str
    k: int = 3  # cantidad de vecinos a devolver


class LocationResult(BaseModel):
    id: int
    name: str
    lat: float
    lng: float
    address: str
    contact: str
    distance: float


class NearbyResponse(BaseModel):
    address: str
    lat: float
    lng: float
    neighbors: list[LocationResult]
