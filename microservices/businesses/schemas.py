from pydantic import BaseModel
from datetime import date
from typing import Optional


class UserBase(BaseModel):
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    email: str


class UserCreate(UserBase):
    pass


class User(UserBase):
    user_id: int

    class Config:
        orm_mode = True


class TicketBase(BaseModel):
    user_id: int
    description: str
    closed: Optional[bool] = False


class TicketCreate(TicketBase):
    pass


class Ticket(TicketBase):
    ticket_id: int
    date_created: str

    class Config:
        orm_mode = True


class ListBase(BaseModel):
    user_id: int
    location: str
    date: str
    description: Optional[str] = None


class ListCreate(ListBase):
    user_id: int
    location: str
    date: str
    description: Optional[str] = None


class List(ListBase):
    list_id: int

    class Config:
        orm_mode = True


class BusinessBase(BaseModel):
    business_name: str
    location: str
    address: str
    category: str
    description: str


class BusinessCreate(BusinessBase):
    # Define the Pydantic model for the request body
    class BusinessCreate(BaseModel):
        business_name: str
        location: str
        address: str
        category: str
        description: str

class BusinessUpdate(BaseModel):
    business_name: Optional[str] = None
    location: Optional[str] = None
    address: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None

    class Config:
        orm_mode = True

class Business(BusinessBase):
    business_id: int

    class Config:
        orm_mode = True

class ItineraryBase(BaseModel):
    list_id: int
    business_id: int

class ItineraryCreate(ItineraryBase):
    pass

class Itinerary(ItineraryBase):
    class Config:
        orm_mode = True
