from fastapi import FastAPI, Depends, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import crud
import database
import schemas
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
#from fastapi.responses import Response
import time
from typing import List
import logging
#from dotenv import load_dotenv
import set_env
import os
import uvicorn
import uuid

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


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("tracing.log"),  # Log to a file
        logging.StreamHandler(),            # Log to the console
    ],
)

# Custom Logging, Tracing, and Correlation ID Middleware
class TracingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Generate or extract Correlation ID
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        request.state.correlation_id = correlation_id

        # Start timing the request
        start_time = time.time()

        # Log request details
        logging.info(f"Request Start: {request.method} {request.url}")
        logging.info(f"Correlation ID: {correlation_id} - {request.method} {request.url}")
        logging.info(f"Headers: {request.headers}")

        if request.method in ["POST", "PUT", "PATCH"]:
            body = await request.body()
            logging.info(f"Body: {body.decode('utf-8') if body else None}")

        # Process the request and get the response
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id

        # End timing and log response details
        process_time = time.time() - start_time
        logging.info(
            f"Request End: {request.method} {request.url} - "
            f"Status Code: {response.status_code} - Time: {process_time:.4f}s"
        )

        return response

# Add the middleware to FastAPI
app.add_middleware(TracingMiddleware)

# Dependency to get a database session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def root():
    return {"message": "Tracing middleware is active!"}

@app.post("/lists/", response_model=schemas.List, status_code=201)
def create_list(user_id:int,location:str,date:str,description:str, db: Session = Depends(get_db)):
    # Call the CRUD function to create the resource
    list_data = schemas.ListCreate(
        user_id=user_id,
        location=location,
        date=date,
        description=description
    )
    created_list = crud.create_list(db=db, list_data=list_data)
    """
    # Generate the link to the newly created resource
    resource_id = created_list.list_id
    resource_url = f"/lists/{resource_id}"
    """

    # Add the link or location header
    #response.headers["Location"] = resource_url # Used to point to the new resource

    return created_list


@app.get("/weather/", response_model=str)
def get_weather(location: str, date: str, db: Session = Depends(get_db), request: Request = None):
    correlation_id = request.state.correlation_id
    latitude, longitude = crud.fetch_lat_lon(location, correlation_id)
    return crud.fetch_weather(latitude, longitude, date, correlation_id)

@app.get("/lists/", response_model=List[schemas.List])
def get_lists(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_lists(db=db, skip=skip, limit=limit)

@app.delete("/lists/{list_id}", response_model=schemas.List)
def delete_list(list_id: int, db: Session = Depends(get_db)):
    deleted_list = crud.delete_list(db=db, list_id=list_id)
    if deleted_list is None:
        raise HTTPException(status_code=404, detail="List not found")
    return deleted_list

@app.post("/lists/{list_id}/itineraries/", response_model=schemas.Itinerary, status_code=202)
def add_itinerary_to_list(list_id: int, business_id: int, db: Session = Depends(get_db)):
    return crud.add_itinerary(db=db, list_id=list_id, business_id=business_id)

@app.get("/lists/{list_id}/itineraries/", response_model=List[schemas.Itinerary])
def get_itineraries_for_list(list_id: int, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_itineraries(db=db, list_id=list_id, skip=skip, limit=limit)

@app.delete("/lists/{list_id}/itineraries/{business_id}", response_model=schemas.Itinerary)
def delete_itinerary_from_list(list_id: int, business_id: int, db: Session = Depends(get_db)):
    itinerary = crud.delete_itinerary(db=db, list_id=list_id, business_id=business_id)
    if itinerary is None:
        raise HTTPException(status_code=404, detail="Itinerary not found")
    return itinerary

@app.put("/lists/{list_id}/description", response_model=dict)
def update_list_description(
    list_id: int,
    description: str,  # Accept the description directly as a parameter
    db: Session = Depends(get_db)
):
    updated_list = crud.update_list_description(db=db, list_id=list_id, description=description)
    if updated_list is None:
        raise HTTPException(status_code=404, detail="List not found")
    return {"message": "Description updated successfully", "list_id": list_id, "description": description}

# Run the application with Uvicorn
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)