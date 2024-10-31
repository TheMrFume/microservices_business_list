from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class List(Base):
    __tablename__ = "lists"
    list_id = Column(Integer, primary_key=True, index=True)
    creator_id = Column(Integer, nullable=False)

    # Using string reference for Itinerary to avoid circular dependencies
    itineraries = relationship("Itinerary", back_populates="list", cascade="all, delete-orphan")


class Itinerary(Base):
    __tablename__ = "itineraries"
    itinerary_id = Column(Integer, primary_key=True, index=True)
    list_id = Column(Integer, ForeignKey("lists.list_id"), nullable=False)
    business_id = Column(Integer, nullable=False)
    day = Column(String, nullable=True)  # Optional if no schedule
    times = Column(String, nullable=True)

    # Relationship to link back to List
    list = relationship("List", back_populates="itineraries")