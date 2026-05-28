"""Want list model — buyers specify what coins they're looking for."""

from sqlalchemy import (
    Column, String, Boolean, DateTime, Float, Integer,
    Text, ForeignKey, JSON, func
)
from app.database import Base


class WantListItem(Base):
    """A single 'want' — e.g. 'Morgan Dollar, MS-63+, under $2,000'."""
    __tablename__ = "want_list_items"

    id = Column(String(36), primary_key=True)
    buyer_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    # What they want
    coin_type = Column(String(200), nullable=True)          # "Morgan Dollar"
    series = Column(String(200), nullable=True)             # "Peace Dollar"
    year_min = Column(Integer, nullable=True)               # 1878
    year_max = Column(Integer, nullable=True)               # 1921
    mint_marks = Column(JSON, nullable=True)                # ["S", "CC", "O"]
    denomination = Column(String(100), nullable=True)
    country = Column(String(100), default="United States")
    
    # Grade range
    min_grade_numeric = Column(Integer, nullable=True)      # e.g. 63 for MS-63+
    max_grade_numeric = Column(Integer, nullable=True)      # e.g. 70 for MS-70
    
    # Price range
    price_min = Column(Float, nullable=True)
    price_max = Column(Float, nullable=True)
    
    # Preferences
    must_be_graded = Column(Boolean, default=False)         # PCGS/NGC only?
    accept_ai_graded = Column(Boolean, default=True)
    tags = Column(JSON, nullable=True)                      # ["key_date", "toned"]
    notes = Column(Text, nullable=True)                     # Free-text: "Looking for rainbow toning"
    
    # Status
    is_active = Column(Boolean, default=True)
    notify_immediately = Column(Boolean, default=True)      # Fresh Inventory alert?
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
