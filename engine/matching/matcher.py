"""Standalone matching engine utilities.

The core matching logic lives in backend/app/services/matching.py
(integrated with SQLAlchemy models). This module provides additional
matching utilities for batch processing and background jobs.
"""

from typing import Optional, List, Dict


# Common U.S. coin types and their aliases
COIN_TYPE_ALIASES = {
    "morgan": "morgan dollar",
    "morgan dollar": "morgan dollar",
    "morgan silver dollar": "morgan dollar",
    "peace": "peace dollar",
    "peace dollar": "peace dollar",
    "lincoln": "lincoln cent",
    "lincoln cent": "lincoln cent",
    "lincoln penny": "lincoln cent",
    "wheat penny": "lincoln cent",
    "wheat cent": "lincoln cent",
    "walking liberty": "walking liberty half dollar",
    "walker": "walking liberty half dollar",
    "seated liberty": "seated liberty",
    "barber": "barber",
    "buffalo nickel": "buffalo nickel",
    "mercury dime": "mercury dime",
    "merc": "mercury dime",
    "standing liberty": "standing liberty quarter",
    "washington quarter": "washington quarter",
    "kennedy half": "kennedy half dollar",
    "franklin half": "franklin half dollar",
    "indian head": "indian head cent",
    "saint gaudens": "saint-gaudens",
    "saint-gaudens": "saint-gaudens",
    "double eagle": "saint-gaudens",
    "trade dollar": "trade dollar",
}


def normalize_coin_type(raw: str) -> str:
    """Normalize user-entered coin type to canonical form."""
    if not raw:
        return ""
    lowered = raw.strip().lower()
    return COIN_TYPE_ALIASES.get(lowered, lowered)


# Mint mark normalization
MINT_MARKS = {
    "p": "P",       # Philadelphia
    "d": "D",       # Denver (or Dahlonega for pre-1861 gold)
    "s": "S",       # San Francisco
    "o": "O",       # New Orleans
    "cc": "CC",     # Carson City
    "w": "W",       # West Point
    "c": "C",       # Charlotte (gold only, 1838-1861)
}


def normalize_mint_mark(raw: str) -> str:
    """Normalize mint mark to uppercase standard."""
    if not raw:
        return ""
    return MINT_MARKS.get(raw.strip().lower(), raw.strip().upper())


def format_match_notification(coin: dict, match_score: float, reasons: List[str]) -> str:
    """Format a match notification message for the buyer.
    
    Used for email, push notifications, and Slack alerts.
    """
    title = coin.get("title", "Unknown Coin")
    grade = coin.get("ai_grade", "Ungraded")
    price = coin.get("asking_price") or coin.get("estimated_value")
    is_estate = coin.get("is_estate", False)

    lines = []
    
    if is_estate:
        lines.append("🪙 *Fresh Estate Inventory Alert*")
        lines.append(f"A new estate collection coin has entered the marketplace.")
    else:
        lines.append("🔔 *New Match Found*")
    
    lines.append(f"*{title}*")
    lines.append(f"AI Grade: {grade} | Match Score: {match_score:.0%}")
    
    if price:
        lines.append(f"Price: ${price:,.2f}")
    
    matched_on = ", ".join(reasons)
    lines.append(f"Matched on: {matched_on}")
    
    if is_estate:
        lines.append("\n_Pro and Dealer members get first access to estate inventory._")
    
    return "\n".join(lines)
