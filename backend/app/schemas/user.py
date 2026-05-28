"""User request/response schemas."""

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class UserSignup(BaseModel):
    email: EmailStr
    password: str
    name: str
    user_type: str = "buyer"  # buyer, estate_seller, dealer
    acquisition_trigger: Optional[str] = None  # inherited, downsizing, organic


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    user_type: str
    tier: str
    role: str
    avatar_url: Optional[str] = None
    location_state: Optional[str] = None
    collecting_focus: Optional[list] = None
    estate_alert_opted_in: bool = False
    total_purchases: int = 0
    total_sales: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    location_state: Optional[str] = None
    bio: Optional[str] = None
    collecting_focus: Optional[list] = None
    price_range_min: Optional[float] = None
    price_range_max: Optional[float] = None
    estate_alert_opted_in: Optional[bool] = None
    estate_alert_categories: Optional[list] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
