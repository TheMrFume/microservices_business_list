from pydantic import BaseModel
from typing import Optional


class BusinessBase(BaseModel):
    display_name: str
    description: Optional[str] = None
    password: str
    address: str
    coordinates: Optional[str] = None
    category: Optional[str] = None

    # Operating hours for each day of the week
    mon_hrs: Optional[str] = None
    tue_hrs: Optional[str] = None
    wed_hrs: Optional[str] = None
    thu_hrs: Optional[str] = None
    fri_hrs: Optional[str] = None
    sat_hrs: Optional[str] = None
    sun_hrs: Optional[str] = None


class BusinessCreate(BusinessBase):
    pass


class Business(BusinessBase):
    business_id: int

    class Config:
        from_attributes = True


class BusinessUpdate(BaseModel):
    display_name: Optional[str] = None
    description: Optional[str] = None
    password: Optional[str] = None
    address: Optional[str] = None
    coordinates: Optional[str] = None
    category: Optional[str] = None

    # Operating hours for each day of the week
    mon_hrs: Optional[str] = None
    tue_hrs: Optional[str] = None
    wed_hrs: Optional[str] = None
    thu_hrs: Optional[str] = None
    fri_hrs: Optional[str] = None
    sat_hrs: Optional[str] = None
    sun_hrs: Optional[str] = None
