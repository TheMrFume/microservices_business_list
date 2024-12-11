from sqlalchemy.orm import Session
import models
import schemas
import httpx

def create_list(db: Session, list_data: schemas.ListCreate):
    db_list = models.List(**list_data.model_dump())
    db.add(db_list)
    db.commit()
    db.refresh(db_list)
    return db_list

def get_lists(db: Session, skip: int = 0, limit: int = 10):
    lists = db.query(models.List).offset(skip).limit(limit).all()
    return lists

def delete_list(db: Session, list_id: int):
    db_list = db.query(models.List).filter(models.List.list_id == list_id).first()
    if db_list:
        db.delete(db_list)
        db.commit()
        return db_list
    return None

def fetch_lat_lon(location: str, correlation_id: str) -> tuple:
    base_url = "https://nominatim.openstreetmap.org/search"
    headers = {"X-Correlation-ID": correlation_id}
    params = {
        "q": location,
        "format": "json",
        "limit": 1,
    }
    response = httpx.get(base_url, headers=headers, params=params)
    if response.status_code == 200 and response.json():
        data = response.json()[0]
        latitude = float(data["lat"])
        longitude = float(data["lon"])
        return latitude, longitude
    raise Exception("Could not fetch latitude and longitude for the given location")

def fetch_weather(latitude: float, longitude: float, date: str, correlation_id: str) -> str:
    api_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&start_date={date}&end_date={date}&daily=temperature_2m_max,temperature_2m_min"
    headers = {"X-Correlation-ID": correlation_id}
    response = httpx.get(api_url, headers = headers)
    if response.status_code == 200:
        data = response.json()
        avg_temp = (data["daily"]["temperature_2m_max"][0] + data["daily"]["temperature_2m_min"][0]) / 2
        return str(avg_temp)


def add_itinerary(db: Session, list_id: int, business_id: int):
    db_list = db.query(models.List).filter(models.List.list_id == list_id).first()
    if not db_list:
        raise Exception("List not found")

    db_itinerary = models.Itinerary(list_id=list_id, business_id=business_id)
    db.add(db_itinerary)
    db.commit()
    return db_itinerary

def get_itineraries(db: Session, list_id: int, skip: int = 0, limit: int = 10):
    itineraries = db.query(models.Itinerary).filter(models.Itinerary.list_id == list_id).offset(skip).limit(limit).all()
    return itineraries

def delete_itinerary(db: Session, list_id: int, business_id: int):
    db_itinerary = db.query(models.Itinerary).filter(
        models.Itinerary.list_id == list_id,
        models.Itinerary.business_id == business_id
    ).first()
    if db_itinerary:
        db.delete(db_itinerary)
        db.commit()
        return db_itinerary
    return None

def update_list_description(db: Session, list_id: int, description: str):
    db_list = db.query(models.List).filter(models.List.list_id == list_id).first()
    if not db_list:
        return None  # Return None if the list is not found
    db_list.description = description  # Update only the description field
    db.commit()
    db.refresh(db_list)  # Refresh to get the latest data
    return db_list  # Return the updated list
