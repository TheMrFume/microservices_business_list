from fastapi import FastAPI, HTTPException, Depends
from typing import List, Optional
import crud
import database
import schemas
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables from .env
dotenv_path = os.path.join(os.path.dirname(__file__), '..', ".env")
load_dotenv(dotenv_path)

app = FastAPI(debug=True)

# Setup CORS using environment variables, if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ALLOW_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get a database session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/businesses/", response_model=schemas.Business)
def create_business(business: schemas.BusinessCreate, db: Session = Depends(get_db)):
    return crud.create_business(db=db, business=business)

@app.get("/businesses/", response_model=List[schemas.Business])
def get_businesses(skip: int = 0, limit: int = 10, address: Optional[str] = None, db: Session = Depends(get_db)):
    businesses = crud.get_businesses(db, skip=skip, limit=limit, address=address)
    return businesses

@app.delete("/businesses/{business_id}", response_model=schemas.Business)
def delete_business(business_id: int, db: Session = Depends(get_db)):
    business = crud.delete_business(db=db, business_id=business_id)
    if business is None:
        raise HTTPException(status_code=404, detail="Business not found")
    return business

@app.put("/businesses/{business_id}", response_model=schemas.Business)
def update_business(business_id: int, business_data: schemas.BusinessUpdate, db: Session = Depends(get_db)):
    updated_business = crud.update_business(db=db, business_id=business_id, business_data=business_data)
    if updated_business is None:
        raise HTTPException(status_code=404, detail="Business not found")
    return updated_business
