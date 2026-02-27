from pydantic import BaseModel
from datetime import date

class VerseResponse(BaseModel):
    verse: str
    resume: str


class DailyVerseResponse(BaseModel):
    id: int
    date: date
    resume: str
    verse: str

    class Config:
        from_attributes = True