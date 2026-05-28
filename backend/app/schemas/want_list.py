"""Want list request/response schemas."""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class WantListCreate(BaseModel):
    coin_type: Optional[str] = None
    series: Optional[str] = None
    year_min: Optional[int] = None
    year_max: Optional[int] = None
    mint_marks: Optional[List[str]] = None
    denomination: Optional[str] = None
    country: str = "United States"
    min_grade_numeric: Optional[int] = None
    max_grade_numeric: Optional[int] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    must_be_graded: bool = False
    accept_ai_graded: bool = True
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    notify_immediately: bool = True


class WantListResponse(BaseModel):
    id: str
    buyer_id: str
    coin_type: Optional[str] = None
    series: Optional[str] = None
    year_min: Optional[int] = None
    year_max: Optional[int] = None
    mint_marks: Optional[list] = None
    denomination: Optional[str] = None
    country: str
    min_grade_numeric: Optional[int] = None
    max_grade_numeric: Optional[int] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    must_be_graded: bool
    accept_ai_graded: bool
    tags: Optional[list] = None
    notes: Optional[str] = None
    notify_immediately: bool
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class WantListUpdate(BaseModel):
    coin_type: Optional[str] = None
    series: Optional[str] = None
    year_min: Optional[int] = None
    year_max: Optional[int] = None
    mint_marks: Optional[List[str]] = None
    denomination: Optional[str] = None
    min_grade_numeric: Optional[int] = None
    max_grade_numeric: Optional[int] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    notify_immediately: Optional[bool] = None
    is_active: Optional[bool] = None
