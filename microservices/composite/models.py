from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Itinerary(Base):
    __tablename__ = "itineraries"
    itinerary_id = Column(Integer, primary_key=True, index=True)
    list_id = Column(Integer, ForeignKey("lists.list_id"), nullable=False)  # Added list_id
    business_id = Column(Integer, nullable=False)  # Reference to business ID
    day = Column(String, nullable=False)  # Day of the week (e.g., "mon", "tue")
    times = Column(String, nullable=False)  # Time blocks in "HH:MM-HH:MM" format, separated by commas

    # Relationship to link back to the list
    list = relationship("List", back_populates="itineraries")
