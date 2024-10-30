from sqlalchemy import Column, Integer, String, Float
from database import Base


class Business(Base):
    __tablename__ = "businesses"

    business_id = Column(Integer, primary_key=True, index=True)
    display_name = Column(String, nullable=False, index=True)
    password = Column(String, nullable=False)
    address = Column(String, nullable=False)
    coordinates = Column(String, nullable=True)  # Assuming coordinates might be stored as a string (e.g., "lat,lng")
    category = Column(String, nullable=True)
    description = Column(String, nullable=True)

    # Operating hours for each day of the week
    mon_hrs = Column(String, nullable=True)
    tue_hrs = Column(String, nullable=True)
    wed_hrs = Column(String, nullable=True)
    thu_hrs = Column(String, nullable=True)
    fri_hrs = Column(String, nullable=True)
    sat_hrs = Column(String, nullable=True)
    sun_hrs = Column(String, nullable=True)
