from pydantic import BaseModel
from datetime import datetime


class SyncResult(BaseModel):
    total_calendar_events: int
    matched: int
    updated_in_wordpress: int
    skipped: int
    errors: list[str]


class CalendarEventMappingBase(BaseModel):
    calendar_title: str
    wordpress_event_id: int
    active: int = 1


class CalendarEventMappingResponse(CalendarEventMappingBase):
    id: int

    class Config:
        from_attributes = True