from app.config import settings
import googlemaps


# ✅ Así debe quedar
async def geocode_address(address: str) -> tuple[float, float]:
    gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
    
    try:
        geocode_result = gmaps.geocode(address)
    except Exception as e:
        raise ValueError(f"Error al conectar con Google Maps: {e}")

    if not geocode_result:
        raise ValueError(f"No se encontró la dirección: {address!r}")

    try:
        lat = geocode_result[0]['geometry']['location']['lat']
        lng = geocode_result[0]['geometry']['location']['lng']
        return lat, lng
    except (KeyError, IndexError) as e:
        raise ValueError(f"Respuesta inesperada de Google Maps: {e}")