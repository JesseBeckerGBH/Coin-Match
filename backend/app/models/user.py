"""User model — supports buyers, sellers, estate sellers, and dealers."""

from sqlalchemy import (
    Column, String, Boolean, DateTime, Float, Integer,
    Text, Enum as SAEnum, JSON, func
)
from app.database import Base
import enum


class UserType(str, enum.Enum):
    BUYER = "buyer"
    ACTIVE_SELLER = "active_seller"
    ESTATE_SELLER = "estate_seller"
    DEALER = "dealer"


class SubscriptionTier(str, enum.Enum):
    FREE = "free"
    PRO = "pro"           # $19/mo
    DEALER = "dealer"     # $99/mo


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)  # null for OAuth users
    name = Column(String(255), nullable=False)
    
    # Persona
    user_type = Column(SAEnum(UserType), default=UserType.BUYER, nullable=False)
    acquisition_trigger = Column(String(50), nullable=True)  # inherited, downsizing, organic, etc.
    age_bracket = Column(String(20), nullable=True)          # '18-24', '25-34', etc.
    
    # Subscription
    tier = Column(SAEnum(SubscriptionTier), default=SubscriptionTier.FREE, nullable=False)
    stripe_customer_id = Column(String(255), nullable=True, unique=True)
    stripe_connect_account_id = Column(String(255), nullable=True, unique=True)
    stripe_subscription_id = Column(String(255), nullable=True)
    
    # Profile
    role = Column(String(20), default="user")  # user, admin
    avatar_url = Column(String(500), nullable=True)
    phone = Column(String(20), nullable=True)
    location_state = Column(String(50), nullable=True)
    location_country = Column(String(50), default="US")
    bio = Column(Text, nullable=True)
    
    # Collector profile enrichment
    collecting_focus = Column(JSON, nullable=True)      # ["morgan_dollars", "lincoln_cents"]
    price_range_min = Column(Float, nullable=True)
    price_range_max = Column(Float, nullable=True)
    estate_alert_opted_in = Column(Boolean, default=False)
    estate_alert_categories = Column(JSON, nullable=True)  # coin types they want alerts for
    
    # Engagement
    engagement_score = Column(Float, default=0.0)
    ltv_estimate = Column(Float, default=0.0)
    total_purchases = Column(Integer, default=0)
    total_sales = Column(Integer, default=0)
    
    # Auth
    google_id = Column(String(255), nullable=True, unique=True)
    email_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)
