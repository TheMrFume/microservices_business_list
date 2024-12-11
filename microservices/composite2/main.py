import asyncio
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from fastapi.responses import Response
import uuid
import uvicorn
import httpx
import json

app = FastAPI()

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
        # Extract and validate the token from the header
        raw_token = request.headers.get("X-Token")
        if not raw_token:
            logging.error("Access denied: Missing X-Token header.")
            raise HTTPException(status_code=400, detail="Access denied: Missing token.")

        try:
            # Parse the token value as JSON
            token_data = json.loads(raw_token)
            user_token = token_data.get("user_token")
            user_id = token_data.get("user_id")

            # Validate that both user_token and user_id are present
            if not user_token or not user_id:
                logging.error("Access denied: Malformed token.")
                raise HTTPException(status_code=400, detail="Access denied: Malformed token.")

            # Store the token in request.state for propagation
            request.state.user_token = user_token
            request.state.user_id = user_id

        except (json.JSONDecodeError, TypeError):
            logging.error("Access denied: Invalid token format.")
            raise HTTPException(status_code=400, detail="Access denied: Invalid token format.")

        # Generate or extract Correlation ID
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        request.state.correlation_id = correlation_id

        # Start timing the request
        start_time = time.time()

        # Log request details
        logging.info(f"Request Start: {request.method} {request.url}")
        logging.info(f"Correlation ID: {correlation_id} - {request.method} {request.url}")
        logging.info(f"Headers: {request.headers}")

        # Process the request
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id

        # Log response details
        process_time = time.time() - start_time
        logging.info(
            f"Request End: {request.method} {request.url} - "
            f"Status Code: {response.status_code} - Time: {process_time:.4f}s"
        )

        return response

# Add the middleware to FastAPI
app.add_middleware(TracingMiddleware)

# Configuration for microservice URLs
BUSINESS_SERVICE_URL = "http://127.0.0.1:8002/businesses"
LIST_SERVICE_URL = "http://127.0.0.1:8001/lists"

# View Full List - Asynchronous Composite Endpoint
@app.get("/composite/view_full_list", response_model=List[dict])
async def view_full_list(list_id: int, request: Request):
    token = {"X-Token": json.dumps({"user_token": request.state.user_token, "user_id": request.state.user_id})}
    correlation_id = {"X-Correlation-ID": request.state.correlation_id}

    headers = {**token, **correlation_id}

    async with httpx.AsyncClient() as client:
        # Step 1: Get all business_ids from the list microservice
        list_url = f"{LIST_SERVICE_URL}/{list_id}/itineraries"
        list_response = await client.get(list_url, headers=headers)

        if list_response.status_code != 200:
            raise HTTPException(status_code=list_response.status_code, detail="Failed to fetch business IDs.")

        business_ids = [item["business_id"] for item in list_response.json()]

        # Step 2: Fetch business details asynchronously from the business microservice
        tasks = [client.get(f"{BUSINESS_SERVICE_URL}/{business_id}", headers=headers) for business_id in business_ids]
        responses = await asyncio.gather(*tasks)

        # Step 3: Compile the details for valid responses
        businesses = [response.json() for response in responses if response.status_code == 200]

    return businesses

# Serve Next - Synchronous Composite Endpoint
@app.get("/composite/serve_next", response_model=dict)
def serve_next(list_id: int, location: str, request: Request):
    token = {"X-Token": json.dumps({"user_token": request.state.user_token, "user_id": request.state.user_id})}
    correlation_id = {"X-Correlation-ID": request.state.correlation_id}

    headers = {**token, **correlation_id}

    with httpx.Client() as client:
        # Step 1: Get all business_ids from the list microservice
        list_url = f"{LIST_SERVICE_URL}/{list_id}/itineraries"
        list_response = client.get(list_url, headers=headers)

        if list_response.status_code != 200:
            raise HTTPException(status_code=list_response.status_code, detail="Failed to fetch business IDs.")

        existing_business_ids = [item["business_id"] for item in list_response.json()]

        # Step 2: Request the next business from the business microservice
        next_business_url = f"{BUSINESS_SERVICE_URL}/next"
        payload = {"list_id": list_id, "location": location, "existing_ids": existing_business_ids}
        next_business_response = client.get(next_business_url, headers=headers, params=payload)

        if next_business_response.status_code != 200:
            raise HTTPException(status_code=next_business_response.status_code, detail="No next business found.")

    return next_business_response.json()


# Run the application with Uvicorn
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8003, reload=True)