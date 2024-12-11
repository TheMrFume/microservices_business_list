from sqlalchemy import Column, Integer, String, Text, ForeignKey, TIMESTAMP, Date, Boolean
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(255), nullable=False)
    middle_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)

    tickets = relationship("Ticket", back_populates="user")
    lists = relationship("List", back_populates="user")


class Ticket(Base):
    __tablename__ = "tickets"

    ticket_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    date_created = Column(TIMESTAMP, nullable=False)
    description = Column(Text, nullable=False)
    closed = Column(Boolean, default=False)

    user = relationship("User", back_populates="tickets")


class List(Base):
    __tablename__ = "lists"

    list_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    location = Column(String(255), nullable=False)
    date = Column(Date, nullable=False)
    description = Column(Text, nullable=True)

    user = relationship("User", back_populates="lists")
    itineraries = relationship("Itinerary", back_populates="list")


class Itinerary(Base):
    __tablename__ = "itineraries"

    list_id = Column(Integer, ForeignKey("lists.list_id"), primary_key=True)
    business_id = Column(Integer, ForeignKey("businesses.business_id"), primary_key=True)

    list = relationship("List", back_populates="itineraries")
    business = relationship("Business", back_populates="itineraries")


class Business(Base):
    __tablename__ = "businesses"

    business_id = Column(Integer, primary_key=True, index=True)
    business_name = Column(String(255), nullable=False)
    location = Column(String(255), nullable=False)
    address = Column(String(255), nullable=False)
    category = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)

    itineraries = relationship("Itinerary", back_populates="business")
