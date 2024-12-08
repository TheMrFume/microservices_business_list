from urllib.request import Request

from fastapi import FastAPI, HTTPException, Depends
from typing import List, Optional
import crud
import database
import schemas
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
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

# Custom Logging Middleware
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        logging.info(
            f"Request: {request.method} {request.url} - "
            f"Response: {response.status_code} - Time: {process_time:.4f}s"
        )
        return response

app.add_middleware(LoggingMiddleware)

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
    business_list = [
        {
            **business.__dict__,
            "links": {
                "self": f"/businesses/{business.business_id}",
                "update": f"/businesses/{business.business_id}",
                "delete": f"/businesses/{business.business_id}",
            },
        }
        for business in businesses
    ]
    return {"data": business_list}

@app.get("/businesses/{business_id}", response_model=schemas.Business)
def get_business(business_id: int, db: Session = Depends(get_db)):
    business = crud.get_business(db, business_id=business_id)
    if business is None:
        raise HTTPException(status_code=404, detail="Business not found")
    return {
        **business.__dict__,
        "links": {
            "self": f"/businesses/{business.business_id}",
            "update": f"/businesses/{business.business_id}",
            "delete": f"/businesses/{business.business_id}",
        },
    }
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

# Run the application with Uvicorn
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)