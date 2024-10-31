from sqlalchemy.orm import Session
import models
import schemas


def create_list(db: Session, list_data: schemas.ListCreate):
    db_list = models.List(**list_data.dict())
    db.add(db_list)
    db.commit()
    db.refresh(db_list)
    return db_list


def get_list(db: Session, list_id: int):
    return db.query(models.List).filter(models.List.list_id == list_id).first()


def update_list(db: Session, list_id: int, list_data: schemas.ListUpdate):
    db_list = db.query(models.List).filter(models.List.list_id == list_id).first()
    if not db_list:
        return None

    if list_data.creator_id is not None:
        db_list.creator_id = list_data.creator_id

    db.commit()
    db.refresh(db_list)
    return db_list


def delete_list(db: Session, list_id: int):
    """
    Deletes a specific list by its ID. Optionally, you may choose to delete all related itineraries
    associated with this list to maintain database integrity.
    """
    # Find the list by its ID
    list_to_delete = db.query(models.List).filter(models.List.list_id == list_id).first()

    if not list_to_delete:
        return None  # Return None if the list doesn't exist

    # Optional: Delete associated itineraries
    db.query(models.Itinerary).filter(models.Itinerary.list_id == list_id).delete()

    # Delete the list
    db.delete(list_to_delete)
    db.commit()

    return list_to_delete
