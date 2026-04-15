from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class TradeItemCreate(BaseModel):
    title: str
    category: str  # furniture/appliance/other
    price: float
    condition: str  # new/like_new/good/fair
    images: List[str]
    description: str
    location: str

class TradeItemResponse(BaseModel):
    id: str
    title: str
    category: str
    price: float
    condition: str
    images: List[str]
    description: str
    location: str
    seller_id: str
    status: str
    created_at: str

class OrderCreate(BaseModel):
    item_id: str

class OrderResponse(BaseModel):
    order_id: str
    item_id: str
    item_type: str
    buyer_id: str
    seller_id: str
    price: float
    status: str
    payment_method: Optional[str]
    created_at: str
