from pydantic import BaseModel
from typing import Optional, List as PydanticList
import sys, os

# Add the path to the module you want to import
module_path = os.path.abspath(os.path.join('../', 'composite'))
sys.path.append(module_path)
from schema import Itinerary

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
        from_attributes = True