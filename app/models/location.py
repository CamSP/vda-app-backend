from dataclasses import dataclass


@dataclass
class Location:
    id: int
    name: str
    lat: float
    lng: float
    address: str
    contact: str
