from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import crud
import database
import schemas
from sqlalchemy.orm import Session
#from dotenv import load_dotenv
import set_env
import os

"""
# Load environment variables from .env
dotenv_path = os.path.join(os.path.dirname(__file__), '..', ".env")
load_dotenv(dotenv_path)
"""

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

@app.post("/lists/", response_model=schemas.List)
def create_list(list_data: schemas.ListCreate, db: Session = Depends(get_db)):
    return crud.create_list(db=db, list_data=list_data)

@app.get("/lists/{list_id}", response_model=schemas.List)
def get_list(list_id: int, db: Session = Depends(get_db)):
    db_list = crud.get_list(db, list_id=list_id)
    if db_list is None:
        raise HTTPException(status_code=404, detail="List not found")
    return db_list

@app.put("/lists/{list_id}", response_model=schemas.List)
def update_list(list_id: int, list_data: schemas.ListUpdate, db: Session = Depends(get_db)):
    return crud.update_list(db=db, list_id=list_id, list_data=list_data)

@app.delete("/lists/{list_id}", response_model=schemas.List)
def delete_list(list_id: int, db: Session = Depends(get_db)):
    db_list = crud.delete_list(db=db, list_id=list_id)
    if db_list is None:
        raise HTTPException(status_code=404, detail="List not found")
    return db_list
