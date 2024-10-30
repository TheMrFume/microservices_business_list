from pydantic import BaseModel
from typing import Optional, List as PydanticList
from microservices.composite.schema import Itinerary

class ListBase(BaseModel):
    creator_id: int

class ListCreate(ListBase):
    pass  # Only creator_id is required for creating a list

class ListUpdate(BaseModel):
    creator_id: Optional[int] = None  # Allow updating creator ID

class List(ListBase):
    list_id: int
    itineraries: PydanticList[Itinerary] = []  # List of associated Itinerary entries (businesses with order) for each day

    class Config:
        orm_mode = True