"""Transaction and match models — the heart of the marketplace."""

from sqlalchemy import (
    Column, String, Boolean, DateTime, Float, Integer,
    Text, ForeignKey, Enum as SAEnum, JSON, func
)
from app.database import Base
import enum


class MatchStatus(str, enum.Enum):
    PENDING = "pending"           # Match found, buyer not yet notified
    NOTIFIED = "notified"         # Buyer received alert
    INTERESTED = "interested"     # Buyer expressed interest
    DECLINED = "declined"         # Buyer passed
    EXPIRED = "expired"           # Timed out


class TransactionStatus(str, enum.Enum):
    INITIATED = "initiated"
    PAYMENT_PENDING = "payment_pending"
    PAYMENT_RECEIVED = "payment_received"
    SHIPPING = "shipping"
    DELIVERED = "delivered"
    COMPLETED = "completed"
    DISPUTED = "disputed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class Match(Base):
    """When a coin listing matches a buyer's want list."""
    __tablename__ = "matches"

    id = Column(String(36), primary_key=True)
    coin_id = Column(String(36), ForeignKey("coins.id"), nullable=False, index=True)
    buyer_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    want_list_item_id = Column(String(36), ForeignKey("want_list_items.id"), nullable=True)
    
    # Match quality
    match_score = Column(Float, nullable=True)              # 0.0-1.0 relevance
    match_reasons = Column(JSON, nullable=True)             # ["coin_type", "grade", "price"]
    
    status = Column(SAEnum(MatchStatus), default=MatchStatus.PENDING, nullable=False)
    
    notified_at = Column(DateTime(timezone=True), nullable=True)
    responded_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Transaction(Base):
    """A completed or in-progress sale between buyer and seller."""
    __tablename__ = "transactions"

    id = Column(String(36), primary_key=True)
    coin_id = Column(String(36), ForeignKey("coins.id"), nullable=False, index=True)
    seller_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    buyer_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    match_id = Column(String(36), ForeignKey("matches.id"), nullable=True)
    
    # Money
    sale_amount = Column(Float, nullable=False)
    commission_rate = Column(Float, nullable=False)         # e.g. 0.035 for 3.5%
    platform_fee = Column(Float, nullable=False)            # Dollar amount
    seller_payout = Column(Float, nullable=False)           # sale_amount - platform_fee
    
    # Stripe
    stripe_payment_intent_id = Column(String(255), nullable=True)
    stripe_transfer_id = Column(String(255), nullable=True)
    
    # Shipping
    tracking_number = Column(String(255), nullable=True)
    shipping_carrier = Column(String(100), nullable=True)
    shipped_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    
    status = Column(SAEnum(TransactionStatus), default=TransactionStatus.INITIATED, nullable=False)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)


class EstateEvent(Base):
    """Tracks estate seller leads from scraping and organic signup."""
    __tablename__ = "estate_events"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    
    trigger_source = Column(String(50), nullable=False)     # reddit_post, signup_form, scraper_flag
    trigger_url = Column(String(1000), nullable=True)
    collection_description = Column(Text, nullable=True)
    collection_est_value = Column(Float, nullable=True)
    
    status = Column(String(20), default="new")              # new, contacted, listed, sold
    
    contacted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
