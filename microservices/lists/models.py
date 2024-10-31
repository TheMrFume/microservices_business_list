from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
#from microservices.composite.models import Itinerary  # Import Itinerary model

class List(Base):
    __tablename__ = "lists"
    list_id = Column(Integer, primary_key=True, index=True)
    creator_id = Column(Integer, nullable=False)  # Reference to user ID or owner

    # Relationship with Itinerary (acts as the queue of businesses in the list)
    itineraries = relationship("Itinerary", back_populates="list", cascade="all, delete-orphan", order_by="Itinerary.order_no")
