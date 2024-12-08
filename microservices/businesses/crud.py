from sqlalchemy.orm import Session
import models
import schemas

def create_business(db: Session, business: schemas.BusinessCreate):
    db_business = models.Business(**business.model_dump())
    db.add(db_business)
    db.commit()
    db.refresh(db_business)
    return {
        **db_business.__dict__,
        "links": {
            "self": f"/businesses/{db_business.business_id}",
            "update": f"/businesses/{db_business.business_id}",
            "delete": f"/businesses/{db_business.business_id}",
        },
    }

def get_businesses(db: Session, skip: int = 0, limit: int = 10, address: str = None):
    query = db.query(models.Business)
    if address:
        query = query.filter(models.Business.address == address)
    return query.offset(skip).limit(limit).all()

def get_business(db: Session, business_id: int):
    return db.query(models.Business).filter(models.Business.business_id == business_id).first()

def delete_business(db: Session, business_id: int):
    business = db.query(models.Business).filter(models.Business.business_id == business_id).first()
    if business:
        db.delete(business)
        db.commit()
        return business
    else:
        return None

def update_business(db: Session, business_id: int, business_data: schemas.BusinessUpdate):
    db_business = db.query(models.Business).filter(models.Business.business_id == business_id).first()
    if db_business:
        for key, value in business_data.model_dump(exclude_unset=True).items():
            setattr(db_business, key, value)
        db.commit()
        db.refresh(db_business)
        return {
            **db_business.__dict__,
            "links": {
                "self": f"/businesses/{db_business.business_id}",
                "update": f"/businesses/{db_business.business_id}",
                "delete": f"/businesses/{db_business.business_id}",
            },
        }
    return None
