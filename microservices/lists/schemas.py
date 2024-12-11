from pydantic import BaseModel
from typing import Optional

class ListBase(BaseModel):
    user_id: int
    location: str
    date: str
    description: Optional[str] = None

class ListCreate(ListBase):
    pass

class List(ListBase):
    list_id: int

    class Config:
        orm_mode = True

class ListUpdate(BaseModel):
    location: Optional[str] = None
    description: Optional[str] = None

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
