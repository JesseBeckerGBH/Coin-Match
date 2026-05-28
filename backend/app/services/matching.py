"""Matching engine — connects coins to buyer want lists.

When an estate seller uploads a coin:
1. AI grades it
2. This engine finds all matching want-list items
3. Pro/Dealer subscribers get "Fresh Inventory" alerts first
4. Free buyers see it after a 24-hour delay
"""

import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session

from app.models.coin import Coin, CoinStatus
from app.models.want_list import WantListItem
from app.models.transaction import Match, MatchStatus
from app.models.user import User, SubscriptionTier


def find_matches(db: Session, coin: Coin) -> list[dict]:
    """Find all want-list items that match a given coin.
    
    Returns list of matches sorted by match_score (best first).
    """
    query = db.query(WantListItem).filter(WantListItem.is_active == True)
    
    # Don't match the seller with their own wants
    query = query.filter(WantListItem.buyer_id != coin.seller_id)
    
    candidates = query.all()
    matches = []
    
    for want in candidates:
        score, reasons = _score_match(coin, want)
        if score > 0:
            matches.append({
                "want_list_item": want,
                "score": score,
                "reasons": reasons,
            })
    
    # Sort by score descending
    matches.sort(key=lambda m: m["score"], reverse=True)
    return matches


def _score_match(coin: Coin, want: WantListItem) -> tuple[float, list[str]]:
    """Score how well a coin matches a want-list item. 0 = no match, 1.0 = perfect."""
    score = 0.0
    reasons = []
    max_points = 0
    
    # Coin type match (highest weight)
    if want.coin_type:
        max_points += 3
        if coin.coin_type and want.coin_type.lower() in coin.coin_type.lower():
            score += 3
            reasons.append("coin_type")
    
    # Series match
    if want.series:
        max_points += 2
        if coin.series and want.series.lower() in coin.series.lower():
            score += 2
            reasons.append("series")
    
    # Year range
    if want.year_min or want.year_max:
        max_points += 2
        if coin.year:
            in_range = True
            if want.year_min and coin.year < want.year_min:
                in_range = False
            if want.year_max and coin.year > want.year_max:
                in_range = False
            if in_range:
                score += 2
                reasons.append("year")
    
    # Mint mark
    if want.mint_marks:
        max_points += 1
        if coin.mint_mark and coin.mint_mark.upper() in [m.upper() for m in want.mint_marks]:
            score += 1
            reasons.append("mint_mark")
    
    # Grade range
    if want.min_grade_numeric:
        max_points += 2
        grade = coin.ai_grade_numeric or 0
        if grade >= want.min_grade_numeric:
            if not want.max_grade_numeric or grade <= want.max_grade_numeric:
                score += 2
                reasons.append("grade")
    
    # Price range
    if want.price_max:
        max_points += 2
        price = coin.asking_price or coin.estimated_value or 0
        if price > 0:
            in_range = True
            if want.price_min and price < want.price_min:
                in_range = False
            if want.price_max and price > want.price_max:
                in_range = False
            if in_range:
                score += 2
                reasons.append("price")
    
    # Denomination
    if want.denomination:
        max_points += 1
        if coin.denomination and want.denomination.lower() in coin.denomination.lower():
            score += 1
            reasons.append("denomination")
    
    # Country
    if want.country and want.country != "United States":
        max_points += 1
        if coin.country and want.country.lower() == coin.country.lower():
            score += 1
            reasons.append("country")
    
    # Normalize to 0-1
    if max_points == 0:
        return 0.0, []
    
    normalized = score / max_points
    
    # Must have at least coin_type or series match to count
    if "coin_type" not in reasons and "series" not in reasons:
        return 0.0, []
    
    return round(normalized, 3), reasons


def create_matches(db: Session, coin: Coin) -> list[Match]:
    """Find matches for a coin and persist them to the database.
    
    Pro/Dealer buyers are notified immediately.
    Free buyers are notified after 24h delay (handled by a background task).
    """
    raw_matches = find_matches(db, coin)
    created = []
    
    for m in raw_matches:
        want = m["want_list_item"]
        buyer = db.query(User).filter(User.id == want.buyer_id).first()
        if not buyer:
            continue
        
        match = Match(
            id=str(uuid.uuid4()),
            coin_id=coin.id,
            buyer_id=want.buyer_id,
            want_list_item_id=want.id,
            match_score=m["score"],
            match_reasons=m["reasons"],
            status=MatchStatus.PENDING,
        )
        
        # Pro and Dealer subscribers get immediate notification
        if buyer.tier in (SubscriptionTier.PRO, SubscriptionTier.DEALER):
            match.status = MatchStatus.NOTIFIED
            match.notified_at = datetime.now(timezone.utc)
            # TODO: Send push notification / email
        
        db.add(match)
        created.append(match)
    
    if created:
        db.commit()
    
    return created
