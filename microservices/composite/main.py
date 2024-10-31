from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import orchestrator
import crud, models, schema
from database import SessionLocal, engine
#from dotenv import load_dotenv
import set_env

"""
# Load environment variables from .env
dotenv_path = os.path.join(os.path.dirname(__file__), '..', ".env")
load_dotenv(dotenv_path)
"""

# Create tables -> Don't need to, tables already created
# models.Base.metadata.create_all(bind=engine)

app = FastAPI(debug=True)

# Setup CORS using environment variables, if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ALLOW_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Queue Management Endpoints
@app.post("/queue/start/")
async def start_queue(address: str):
    """
    Initializes the business queue with businesses from the specified address.
    """
    try:
        await orchestrator.start_business_queue(address)
        return {"message": "Business queue started successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/queue/end/")
async def end_queue():
    """
    Clears the business queue.
    """
    try:
        await orchestrator.end_business_queue()
        return {"message": "Business queue ended successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/queue/next-business/")
async def get_next_business():
    """
    Retrieves the next business from the queue.
    """
    try:
        next_business = await orchestrator.get_next_business()
        return next_business
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/queue/add-or-remove-business/")
async def add_or_remove_business(user_id: int, business_id: int, list_id: int, address: str, day: str, action: str, db: Session = Depends(get_db)):
    """
    Adds or removes a business from the queue depending on the action specified.
    - If action is "add", the business is added to the user's list as an itinerary.
    - If action is "remove", the business is removed from the queue without being added to the user's list.
    """
    try:
        if action == "add":
            await orchestrator.add_business_to_user_list(db=db, user_id=user_id, business_id=business_id, list_id=list_id, address=address, day=day)
            return {"message": "Business added to user's list and removed from queue"}
        elif action == "remove":
            await orchestrator.remove_business_from_queue(business_id=business_id, address=address)
            return {"message": "Business removed from queue"}
        else:
            raise HTTPException(status_code=400, detail="Invalid action specified. Use 'add' or 'remove'.")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Itinerary CRUD Endpoints

@app.post("/itineraries/", response_model=schema.Itinerary)
def create_itinerary(itinerary: schema.ItineraryCreate, db: Session = Depends(get_db)):
    """
    Creates a new itinerary entry, adding a business to a list for a specific day and time.
    """
    return crud.create_itinerary(db=db, itinerary_data=itinerary)

@app.get("/itineraries/{list_id}", response_model=List[schema.Itinerary])
def read_itineraries_by_list(list_id: int, day: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Retrieves all itinerary entries for a specific list, ordered by `times`.
    Optionally filter by a specific `day`.
    """
    itineraries = crud.get_itineraries_by_list(db=db, list_id=list_id, day=day)
    if not itineraries:
        raise HTTPException(status_code=404, detail="No itineraries found for the specified list and day.")
    return itineraries

@app.put("/itineraries/{itinerary_id}/times", response_model=schema.Itinerary)
def update_itinerary_times(itinerary_id: int, times: str, db: Session = Depends(get_db)):
    """
    Updates the `times` of a specific itinerary entry.
    """
    itinerary = crud.update_itinerary_times(db=db, itinerary_id=itinerary_id, times=times)
    if itinerary is None:
        raise HTTPException(status_code=404, detail="Itinerary not found")
    return itinerary

@app.delete("/itineraries/{itinerary_id}", response_model=schema.Itinerary)
def delete_itinerary(itinerary_id: int, db: Session = Depends(get_db)):
    """
    Deletes a specific itinerary entry.
    """
    itinerary = crud.delete_itinerary(db=db, itinerary_id=itinerary_id)
    if itinerary is None:
        raise HTTPException(status_code=404, detail="Itinerary not found")
    return itinerary
