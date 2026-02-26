from app.config import settings
import googlemaps


async def geocode_address(address: str) -> tuple[float, float]:
    """
    Recibe una dirección en texto y devuelve (lat, lng)
    usando la API de Geocoding de Google.
    """
    gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)

    # Geocoding an address
    geocode_result = gmaps.geocode(address)

    try:
        return [geocode_result[0]['geometry']['location']['lat'], geocode_result[0]['geometry']['location']['lng']]
    except:
        raise ValueError(f"No se pudo geocodificar la dirección: {address!r} — status: {geocode_result}")