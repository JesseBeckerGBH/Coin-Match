"""Transaction and match schemas."""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class CommissionEstimate(BaseModel):
    sale_amount: float
    commission_rate: float
    commission_rate_pct: str
    platform_fee_usd: float
    seller_net_usd: float


class MatchResponse(BaseModel):
    id: str
    coin_id: str
    buyer_id: str
    match_score: Optional[float] = None
    match_reasons: Optional[list] = None
    status: str
    notified_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TransactionResponse(BaseModel):
    id: str
    coin_id: str
    seller_id: str
    buyer_id: str
    sale_amount: float
    commission_rate: float
    platform_fee: float
    seller_payout: float
    status: str
    tracking_number: Optional[str] = None
    shipping_carrier: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PurchaseRequest(BaseModel):
    coin_id: str
    offered_price: Optional[float] = None  # If None, uses asking_price


class ShippingUpdate(BaseModel):
    tracking_number: str
    shipping_carrier: str = "USPS"
