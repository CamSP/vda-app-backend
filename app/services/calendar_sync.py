import logging
from datetime import datetime, timezone, timedelta
from googleapiclient.discovery import build
from google.oauth2 import service_account
from rapidfuzz import process, fuzz
from sqlalchemy.orm import Session
import httpx

from app.config import settings
from app.models.calendar_mapping import CalendarEventMapping

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
FUZZY_THRESHOLD = 85  # score mínimo para considerar un match válido


# ── Google Calendar ──────────────────────────────────────────────────────────

def _get_calendar_service():
    credentials = service_account.Credentials.from_service_account_file(
        settings.GOOGLE_SERVICE_ACCOUNT_JSON,
        scopes=SCOPES,
    )
    return build("calendar", "v3", credentials=credentials)


def fetch_calendar_events(days: int = 60) -> list[dict]:
    """Trae los eventos del calendario en los próximos `days` días."""
    try:
        service = _get_calendar_service()
        now = datetime.now(timezone.utc)
        time_max = now + timedelta(days=days)

        events_result = service.events().list(
            calendarId=settings.GOOGLE_CALENDAR_ID,
            timeMin=now.isoformat(),
            timeMax=time_max.isoformat(),
            singleEvents=True,
            orderBy="startTime",
        ).execute()

        return events_result.get("items", [])
    except Exception as e:
        logger.error(f"Error al obtener eventos de Google Calendar: {e}")
        raise


# ── Fuzzy matching ───────────────────────────────────────────────────────────

import unicodedata

def _normalize(text: str) -> str:
    """Convierte a minúsculas y elimina acentos."""
    text = text.lower().strip()
    return ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )

def find_mappings(title: str, mappings: list[CalendarEventMapping]) -> list[CalendarEventMapping]:
    title_norm = _normalize(title)
    mapping_titles = list({_normalize(m.calendar_title) for m in mappings})

    result = process.extractOne(title_norm, mapping_titles, scorer=fuzz.ratio)

    if result and result[1] >= FUZZY_THRESHOLD:
        matched_title = result[0]
        return [m for m in mappings if _normalize(m.calendar_title) == matched_title]

    return []

# ── WordPress ────────────────────────────────────────────────────────────────

def update_wordpress_event(wp_event_id: int, start: datetime, end: datetime) -> bool:
    url = f"{settings.WORDPRESS_URL}/wp-json/tribe/events/v1/events/{wp_event_id}"
    headers = {"Authorization": f"Basic {settings.WORDPRESS_API_KEY}"}

    # Primero trae el evento actual para conservar las horas
    try:
        current = httpx.get(url, headers=headers, timeout=10)
        current.raise_for_status()
        current_data = current.json()

        # Extrae las horas actuales del evento en WP
        current_start = datetime.strptime(current_data["start_date"], "%Y-%m-%d %H:%M:%S")
        current_end = datetime.strptime(current_data["end_date"], "%Y-%m-%d %H:%M:%S")

        website = current_data["website"]
        cost_details = current_data["cost_details"]
        cost = current_data["cost"]

    except Exception as e:
        logger.error(f"Error al obtener evento WP {wp_event_id}: {e}")
        return False

    # Ahora actualiza solo con las fechas combinadas
    payload = {
        "start_date": start.strftime("%Y-%m-%d") + " " + current_start.strftime("%H:%M:%S"),
        "end_date": current_end.strftime("%Y-%m-%d %H:%M:%S"),
        "organizer": [2987],
        "website": website,
        "cost_details": cost_details,
        "cost": cost
    }
        

    try:
        response = httpx.patch(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        return True
    except httpx.HTTPStatusError as e:
        logger.error(f"Error HTTP al actualizar WP evento {wp_event_id}: {e.response.status_code} - {e.response.text}")
        return False
    except Exception as e:
        logger.error(f"Error al actualizar WP evento {wp_event_id}: {e}")
        return False


# ── Sync principal ───────────────────────────────────────────────────────────

def sync_calendar(db: Session, days: int = 5) -> dict:
    """
    Flujo completo:
    1. Trae eventos de Google Calendar
    2. Fuzzy match con mappings de la DB
    3. Actualiza fechas en WordPress
    4. El primer match por evento WP gana (ignora duplicados)
    """
    errors = []
    matched = 0
    updated = 0
    skipped = 0
    already_updated: set[int] = set()  # evita sobreescribir con un segundo match

    # 1. Trae eventos del calendario
    try:
        calendar_events = fetch_calendar_events(days=days)
    except Exception as e:
        return {
            "total_calendar_events": 0,
            "matched": 0,
            "updated_in_wordpress": 0,
            "skipped": 0,
            "errors": [str(e)],
        }

    # 2. Carga mappings activos de la DB
    mappings = db.query(CalendarEventMapping).all()

    for event in calendar_events:
        title = event.get("summary", "").strip()
        if not title:
            continue

        matched_mappings = find_mappings(title, mappings)
        if not matched_mappings:
            skipped += 1
            continue

        # Parsea fechas ANTES de iterar los mappings
        try:
            start_str = event["start"].get("dateTime") or event["start"].get("date")
            end_str = event["end"].get("dateTime") or event["end"].get("date")
            start = datetime.fromisoformat(start_str)
            end = datetime.fromisoformat(end_str)
        except (KeyError, ValueError) as e:
            errors.append(f"Error parseando fechas de '{title}': {e}")
            continue

        matched += 1

        for mapping in matched_mappings:
            if mapping.wordpress_event_id in already_updated:
                continue
            success = update_wordpress_event(mapping.wordpress_event_id, start, end)
            if success:
                updated += 1
                already_updated.add(mapping.wordpress_event_id)
            else:
                errors.append(f"No se pudo actualizar WP evento {mapping.wordpress_event_id} para '{title}'")
    return {
        "total_calendar_events": len(calendar_events),
        "matched": matched,
        "updated_in_wordpress": updated,
        "skipped": skipped,
        "errors": errors,
    }