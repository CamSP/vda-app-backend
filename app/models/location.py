from sqlalchemy import Column, Integer, String, Float
from app.database import Base

class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    address = Column(String(200))
    lat = Column(Float)
    lng = Column(Float)
    contact = Column(String(20))