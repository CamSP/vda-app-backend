from pydantic import BaseModel
from datetime import date

class VerseResponse(BaseModel):
    verse: str
    summary: str


class DailyVerseResponse(BaseModel):
    id: int
    date: date
    summary: str
    verse: str
    verse_text: str

    class Config:
        from_attributes = True