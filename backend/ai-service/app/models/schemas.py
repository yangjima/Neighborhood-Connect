from typing import List, Optional

from pydantic import BaseModel, Field


class RentalParams(BaseModel):
    type: Optional[str] = Field(None, description="whole/shared/single")
    location: Optional[str] = Field(None, description="Location name")
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)
    min_area: Optional[float] = Field(None, ge=0)
    max_area: Optional[float] = Field(None, ge=0)
    facilities: Optional[List[str]] = None


class TradeParams(BaseModel):
    category: Optional[str] = Field(
        None, description="furniture/appliance/electronics"
    )
    condition: Optional[str] = Field(None, description="like_new/good/acceptable")
    location: Optional[str] = None
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)


class SmartSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="User's natural language query")
    context: str = Field(..., pattern="^(rental|trade)$", description="Search context: rental or trade")


class SmartSearchResponse(BaseModel):
    success: bool
    data: List[dict]
    total: int
    query_understanding: Optional[str] = None
    applied_filters: Optional[dict] = None
    suggestions: Optional[List[str]] = None
    error: Optional[str] = None
