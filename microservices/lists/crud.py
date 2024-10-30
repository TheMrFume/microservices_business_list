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
