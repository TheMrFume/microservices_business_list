from typing import List

from sqlalchemy.orm import Session
import logging
import models
import schemas
import random

def create_business(db: Session, business_data: schemas.BusinessCreate):
    db_business = models.Business(**business_data.model_dump())
    db.add(db_business)
    db.commit()
    db.refresh(db_business)
    #logging.info(f"Correlation ID: {correlation_id} - Created business with ID: {db_business.business_id}")
    return db_business

def get_business(db: Session, business_id: int):
    business = db.query(models.Business).filter(models.Business.business_id == business_id).first()
    #logging.info(f"Correlation ID: {correlation_id} - Retrieved business with ID: {business_id}")
    return business

def delete_business(db: Session, business_id: int, correlation_id: str):
    business = db.query(models.Business).filter(models.Business.business_id == business_id).first()
    if business:
        db.delete(business)
        db.commit()
        logging.info(f"Correlation ID: {correlation_id} - Deleted business with ID: {business_id}")
        return business
    logging.warning(f"Correlation ID: {correlation_id} - Business with ID: {business_id} not found")
    return None

def update_business(db: Session, business_id: int, business_data: schemas.BusinessUpdate, correlation_id: str):
    db_business = db.query(models.Business).filter(models.Business.business_id == business_id).first()
    if db_business:
        for key, value in business_data.model_dump(exclude_unset=True).items():
            setattr(db_business, key, value)
        db.commit()
        db.refresh(db_business)
        logging.info(f"Correlation ID: {correlation_id} - Updated business with ID: {business_id}")
        return db_business
    logging.warning(f"Correlation ID: {correlation_id} - Business with ID: {business_id} not found")
    return None

def get_next_business(db: Session, location: str, existing_ids: List[int]):
    # Fetch all businesses in the given location
    businesses_in_location = (
        db.query(models.Business)
        .filter(models.Business.location == location)
        .all()
    )

    # Filter out businesses already in the list
    available_businesses = [
        b for b in businesses_in_location if b.business_id not in existing_ids
    ]

    # Return a random business if available
    if available_businesses:
        return random.choice(available_businesses)
    return None
    """
    # Validate that list_id is an integer
    if not isinstance(list_id, int):
        raise ValueError("list_id must be an integer.")

    # Fetch all businesses in the given location
    businesses_in_location = (
        db.query(models.Business)
        .filter(models.Business.location == location)
        .all()
    )

    # Fetch businesses already in the list
    business_ids_in_list = (
        db.query(models.Itinerary.business_id)
        .filter(models.Itinerary.list_id == list_id)
        .all()
    )
    business_ids_in_list = {b_id[0] for b_id in business_ids_in_list}  # Unpack from tuples

    # Exclude businesses already in the list
    available_businesses = [
        b for b in businesses_in_location if b.business_id not in business_ids_in_list
    ]

    # Return a random business if available
    if available_businesses:
        return random.choice(available_businesses)
    return None"""

