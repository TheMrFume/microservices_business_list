import uuid
from urllib.request import Request

from fastapi import FastAPI, HTTPException, Depends, Query
from typing import List, Optional
import crud
import database
import schemas
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import logging
import time
#from dotenv import load_dotenv
import set_env
import os
import uvicorn

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


@app.post("/businesses/", response_model=schemas.Business, status_code=201)
def create_business(
    business_name: str,
    location: str,
    address: str,
    category: str,
    description: str,
    db: Session = Depends(get_db)
):
    # Call the CRUD function to create the business
    business_data = schemas.BusinessCreate(
        business_name=business_name,
        location=location,
        address=address,
        category=category,
        description=description
    )
    created_business = crud.create_business(db=db, business_data=business_data)
    return created_business


@app.get("/businesses/{business_id}", response_model=schemas.Business)
def get_business(business_id: int, db: Session = Depends(get_db)):
    #correlation_id = request.state.correlation_id
    business = crud.get_business(db, business_id=business_id)
    if business is None:
        raise HTTPException(status_code=404, detail="Business not found")
    return business
@app.delete("/businesses/{business_id}", response_model=schemas.Business)
def delete_business(business_id: int, db: Session = Depends(get_db), request: Request = None):
    correlation_id = request.state.correlation_id
    business = crud.delete_business(db=db, business_id=business_id, correlation_id=correlation_id)
    if business is None:
        raise HTTPException(status_code=404, detail="Business not found")
    return business

@app.put("/businesses/{business_id}", response_model=schemas.Business)
def update_business(business_id: int, business_data: schemas.BusinessUpdate, db: Session = Depends(get_db), request: Request = None):
    correlation_id = request.state.correlation_id
    updated_business = crud.update_business(db=db, business_id=business_id, business_data=business_data, correlation_id=correlation_id)
    if updated_business is None:
        raise HTTPException(status_code=404, detail="Business not found")
    return updated_business

@app.get("/businesses/next/", response_model=schemas.Business)
def get_next_business(
    location: str,
    existing_ids: str,
    db: Session = Depends(get_db)
):
    existing_ids_list = []
    if existing_ids!="*":
        existing_ids_list = list(map(int, existing_ids.split(",")))

    next_business = crud.get_next_business(db=db, location=location, existing_ids=existing_ids_list)
    if next_business is None:
        raise HTTPException(
            status_code=404,
            detail="No business found at the location that is not in the list."
        )
    return next_business

# Run the application with Uvicorn
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8002, reload=True)