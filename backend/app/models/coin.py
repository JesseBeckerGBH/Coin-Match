"""Coin listing model — the core marketplace item."""

from sqlalchemy import (
    Column, String, Boolean, DateTime, Float, Integer,
    Text, ForeignKey, Enum as SAEnum, JSON, func
)
from app.database import Base
import enum


class CoinStatus(str, enum.Enum):
    DRAFT = "draft"               # Photos uploaded, not yet listed
    GRADING = "grading"           # AI grading in progress
    LISTED = "listed"             # Active on marketplace
    MATCHED = "matched"           # Buyer matched, pending transaction
    PENDING_PAYMENT = "pending_payment"
    SOLD = "sold"
    WITHDRAWN = "withdrawn"


class CoinCondition(str, enum.Enum):
    """Sheldon scale categories."""
    POOR = "P-1"
    FAIR = "FR-2"
    ABOUT_GOOD = "AG-3"
    GOOD = "G-4"
    GOOD_6 = "G-6"
    VERY_GOOD = "VG-8"
    VERY_GOOD_10 = "VG-10"
    FINE = "F-12"
    FINE_15 = "F-15"
    VERY_FINE = "VF-20"
    VERY_FINE_25 = "VF-25"
    VERY_FINE_30 = "VF-30"
    VERY_FINE_35 = "VF-35"
    EXTRA_FINE = "EF-40"
    EXTRA_FINE_45 = "EF-45"
    ABOUT_UNCIRCULATED = "AU-50"
    AU_53 = "AU-53"
    AU_55 = "AU-55"
    AU_58 = "AU-58"
    MINT_STATE_60 = "MS-60"
    MS_61 = "MS-61"
    MS_62 = "MS-62"
    MS_63 = "MS-63"
    MS_64 = "MS-64"
    MS_65 = "MS-65"
    MS_66 = "MS-66"
    MS_67 = "MS-67"
    MS_68 = "MS-68"
    MS_69 = "MS-69"
    MS_70 = "MS-70"
    UNGRADED = "UNGRADED"


class Coin(Base):
    __tablename__ = "coins"

    id = Column(String(36), primary_key=True)
    seller_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    # Basic info
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    year = Column(Integer, nullable=True)
    mint_mark = Column(String(10), nullable=True)           # P, D, S, O, CC, W, etc.
    denomination = Column(String(100), nullable=True)       # "1 cent", "25 cents", "1 dollar"
    coin_type = Column(String(200), nullable=True)          # "Morgan Dollar", "Lincoln Cent"
    series = Column(String(200), nullable=True)             # "Peace Dollar", "Walking Liberty Half"
    country = Column(String(100), default="United States")
    
    # Grading
    ai_grade = Column(String(10), nullable=True)            # Sheldon scale grade
    ai_grade_numeric = Column(Integer, nullable=True)       # 1-70 numeric
    ai_confidence = Column(Float, nullable=True)            # 0.0-1.0
    ai_luster_score = Column(Float, nullable=True)          # 0-10
    ai_strike_score = Column(Float, nullable=True)          # 0-10
    professional_grade = Column(String(10), nullable=True)  # PCGS/NGC confirmed grade
    grading_service = Column(String(20), nullable=True)     # "PCGS", "NGC"
    cert_number = Column(String(50), nullable=True)         # certification number
    
    # Images
    images = Column(JSON, nullable=True)  # List of image URLs
    # {
    #   "obverse": "url",
    #   "reverse": "url", 
    #   "edge": "url",
    #   "detail": "url",
    #   "additional": ["url1", "url2"]
    # }
    
    # Pricing
    estimated_value = Column(Float, nullable=True)          # AI estimate
    asking_price = Column(Float, nullable=True)             # Seller's asking price (optional)
    sold_price = Column(Float, nullable=True)               # Final sale price
    
    # Marketplace
    status = Column(SAEnum(CoinStatus), default=CoinStatus.DRAFT, nullable=False, index=True)
    is_estate = Column(Boolean, default=False, index=True)  # From estate seller?
    
    # Metal content (for bullion value)
    metal_type = Column(String(50), nullable=True)          # gold, silver, copper, etc.
    weight_grams = Column(Float, nullable=True)
    purity = Column(Float, nullable=True)                   # 0.900 for 90% silver, etc.
    
    # Provenance
    provenance_notes = Column(Text, nullable=True)
    
    # Search optimization
    tags = Column(JSON, nullable=True)  # ["key_date", "error_coin", "toned", "rainbow"]
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    listed_at = Column(DateTime(timezone=True), nullable=True)
    sold_at = Column(DateTime(timezone=True), nullable=True)
