import httpx
from fastapi import HTTPException
import os
from dotenv import load_dotenv
from collections import deque
from sqlalchemy.orm import Session
import crud, schema
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

BUSINESS_SERVICE_URL = os.getenv("BUSINESS_SERVICE_URL")

# Queue to maintain a list of businesses
business_queue = deque()

# Constants
QUEUE_SIZE = 5  # Desired queue size for maintaining a list of businesses

async def start_business_queue(address: str):
    """
    Initializes the business queue with businesses from the specified address.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BUSINESS_SERVICE_URL}?address={address}&limit={QUEUE_SIZE}")
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch businesses")

        businesses = response.json()
        for business in businesses:
            business_queue.append(business)

    # Ensure the queue always has enough items
    await maintain_queue(address)

async def end_business_queue():
    """
    Clears the business queue.
    """
    business_queue.clear()

async def maintain_queue(address: str):
    """
    Ensures that the business queue always has at least QUEUE_SIZE items.
    Avoids adding duplicate businesses.
    """
    existing_ids = {business["business_id"] for business in business_queue}

    if len(business_queue) < QUEUE_SIZE:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BUSINESS_SERVICE_URL}?address={address}&limit={QUEUE_SIZE - len(business_queue)}")
            if response.status_code == 200:
                new_businesses = response.json()
                for business in new_businesses:
                    if business["business_id"] not in existing_ids:  # Avoid duplicates
                        business_queue.append(business)
                        existing_ids.add(business["business_id"])

async def get_next_business():
    """
    Retrieves the next business from the queue and maintains the queue size.
    """
    if not business_queue:
        raise HTTPException(status_code=404, detail="No more businesses available in the queue")

    next_business = business_queue.popleft()  # Get the next business
    await maintain_queue(next_business.get("address", "default"))  # Use address to refill queue if needed
    return next_business

async def add_business_to_user_list(db: Session, user_id: int, business_id: int, list_id: int, address: str, day: str):
    """
    Adds a business to a user's list (itinerary) and removes it from the queue.
    Ensures the queue size remains stable.
    """
    # Prepare itinerary data
    itinerary_data = schema.ItineraryCreate(
        business_id=business_id,
        list_id=list_id,
        day=day,
        times=generate_time_blocks()  # Generate time blocks for visits
    )

    # Pass itinerary data as a dictionary to CRUD function
    crud.create_itinerary(db=db, itinerary_data=itinerary_data)  # Use .dict() to convert Pydantic model to dictionary

    # Remove the business from the queue and maintain the queue size
    await remove_business_from_queue(business_id, address)
    await maintain_queue(address)

async def remove_business_from_queue(business_id: int, address: str):
    """
    Removes a specific business from the queue (e.g., if user skips it).
    Calls maintain_queue to ensure the queue size remains stable.
    """
    # Remove the business with the specified ID from the queue
    for business in list(business_queue):
        if business["business_id"] == business_id:
            business_queue.remove(business)
            break  # Exit once the business is removed

    # Refill the queue if necessary
    await maintain_queue(address)

def generate_time_blocks(start_time="09:00", interval_minutes=120, count=7):
    """
    Generates a list of time blocks in "HH:MM-HH:MM" format for a full day.
    Each block is separated by `interval_minutes`.
    """
    blocks = []
    current_time = datetime.strptime(start_time, "%H:%M")
    for _ in range(count):
        end_time = current_time + timedelta(minutes=interval_minutes)
        blocks.append(f"{current_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')}")
        current_time = end_time
    return ",".join(blocks)
