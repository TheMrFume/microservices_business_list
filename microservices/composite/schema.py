from pydantic import BaseModel
from typing import Optional

class ItineraryBase(BaseModel):
    list_id: int  # Added list_id
    business_id: int
    day: str  # e.g., "mon", "tue", "wed", etc.
    times: str  # e.g., "09:00-11:00,11:00-13:00" (time blocks separated by commas)

class ItineraryCreate(ItineraryBase):
    pass

class ItineraryUpdate(BaseModel):
    times: Optional[str] = None  # Allow updating times

class Itinerary(ItineraryBase):
    itinerary_id: int

    class Config:
        from_attributes = True
