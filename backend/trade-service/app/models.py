from pydantic import BaseModel
from typing import List, Optional

class TradeItem(BaseModel):
    id: str
    title: str
    category: str  # furniture/appliance/electronics
    price: float
    condition: str  # like_new/good/acceptable
    images: List[str]
    description: str
    location: str
    seller_id: str
    status: str  # available/reserved/sold
    created_at: str
    view_count: int = 0
    tags: Optional[List[str]] = []
