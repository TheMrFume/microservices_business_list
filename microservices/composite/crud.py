from sqlalchemy.orm import Session
import models
import schema
from datetime import datetime, timedelta

def create_itinerary(db: Session, itinerary_data: schema.ItineraryCreate):
    db_itinerary = models.Itinerary(**itinerary_data.model_dump())
    db.add(db_itinerary)
    db.commit()
    db.refresh(db_itinerary)
    return db_itinerary

def get_itineraries_by_list(db: Session, list_id: int, day: str = None):
    query = db.query(models.Itinerary).filter(models.Itinerary.list_id == list_id)
    if day:
        query = query.filter(models.Itinerary.day == day)
    return query.order_by(models.Itinerary.times).all()

def update_itinerary_times(db: Session, itinerary_id: int, times: str):
    itinerary = db.query(models.Itinerary).filter(models.Itinerary.itinerary_id == itinerary_id).first()
    if itinerary:
        itinerary.times = times
        db.commit()
        db.refresh(itinerary)
    return itinerary

def delete_itinerary(db: Session, itinerary_id: int):
    itinerary = db.query(models.Itinerary).filter(models.Itinerary.itinerary_id == itinerary_id).first()
    if itinerary:
        db.delete(itinerary)
        db.commit()
    return itinerary
