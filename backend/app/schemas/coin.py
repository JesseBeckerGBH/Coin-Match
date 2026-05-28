"""Coin listing request/response schemas."""

from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime


class CoinCreate(BaseModel):
    title: str
    description: Optional[str] = None
    year: Optional[int] = None
    mint_mark: Optional[str] = None
    denomination: Optional[str] = None
    coin_type: Optional[str] = None
    series: Optional[str] = None
    country: str = "United States"
    asking_price: Optional[float] = None
    metal_type: Optional[str] = None
    weight_grams: Optional[float] = None
    purity: Optional[float] = None
    provenance_notes: Optional[str] = None
    tags: Optional[list] = None


class CoinResponse(BaseModel):
    id: str
    seller_id: str
    title: str
    description: Optional[str] = None
    year: Optional[int] = None
    mint_mark: Optional[str] = None
    denomination: Optional[str] = None
    coin_type: Optional[str] = None
    series: Optional[str] = None
    country: str
    
    # Grading
    ai_grade: Optional[str] = None
    ai_grade_numeric: Optional[int] = None
    ai_confidence: Optional[float] = None
    ai_luster_score: Optional[float] = None
    ai_strike_score: Optional[float] = None
    professional_grade: Optional[str] = None
    grading_service: Optional[str] = None
    
    # Images
    images: Optional[dict] = None
    
    # Pricing
    estimated_value: Optional[float] = None
    asking_price: Optional[float] = None
    
    # Marketplace
    status: str
    is_estate: bool
    
    tags: Optional[list] = None
    
    created_at: datetime
    listed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CoinListResponse(BaseModel):
    coins: List[CoinResponse]
    total: int
    page: int
    per_page: int


class CoinSearchParams(BaseModel):
    coin_type: Optional[str] = None
    series: Optional[str] = None
    year_min: Optional[int] = None
    year_max: Optional[int] = None
    mint_mark: Optional[str] = None
    min_grade: Optional[int] = None
    max_grade: Optional[int] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    is_estate: Optional[bool] = None
    country: Optional[str] = None
    tags: Optional[List[str]] = None
    sort_by: str = "created_at"
    sort_order: str = "desc"
    page: int = 1
    per_page: int = 20


class GradeResult(BaseModel):
    grade: str
    grade_numeric: int
    confidence: float
    luster_score: float
    strike_score: float
    estimated_value: Optional[float] = None
    notes: str = ""
