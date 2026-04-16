from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Location(BaseModel):
    community: str
    address: str
    district: Optional[str] = None
    coordinates: Optional[List[float]] = None

class Rental(BaseModel):
    id: str
    title: str
    type: str  # whole/shared/single
    price: float
    area: float
    location: Location
    facilities: List[str]
    images: List[str]
    description: str
    contact: str
    publisher_id: str
    status: str  # available/reserved/rented
    created_at: str
    view_count: int = 0
    favorite_count: int = 0
