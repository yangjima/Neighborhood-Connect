from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Location(BaseModel):
    community: str
    address: str
    coordinates: Optional[List[float]] = None

class RentalCreate(BaseModel):
    title: str
    type: str  # whole/shared/single
    price: float
    area: float
    location: Location
    facilities: List[str]
    images: List[str]
    description: str
    contact: str

class RentalResponse(BaseModel):
    id: str
    title: str
    type: str
    price: float
    area: float
    location: dict
    facilities: List[str]
    images: List[str]
    description: str
    contact: str
    publisher_id: str
    status: str
    created_at: str

class FavoriteRequest(BaseModel):
    rental_id: str

class AppointmentRequest(BaseModel):
    rental_id: str
    name: str
    phone: str
    visit_time: str
    message: Optional[str] = None
