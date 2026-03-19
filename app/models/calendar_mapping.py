from sqlalchemy import Column, Integer, String
from app.database import Base


class CalendarEventMapping(Base):
    __tablename__ = "calendar_event_mappings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    calendar_title = Column(String(200), nullable=False)
    wordpress_event_id = Column(Integer, nullable=False)
    