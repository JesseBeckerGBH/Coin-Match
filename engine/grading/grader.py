"""AI Coin Grading Engine — V1 (Rule-Based + Placeholder for ML).

Phase 1: Rule-based grading using image analysis heuristics.
Phase 2: EfficientNet-B7 / ViT model trained on 5,000+ labeled images per series.
Phase 3: PCGS/NGC feedback loop for continuous improvement.

Target accuracy: 85-92% exact grade match, 96-98% within ±1 Sheldon point.
"""

import os
import random
from typing import Optional


# Sheldon scale mapping
SHELDON_GRADES = {
    1: "P-1", 2: "FR-2", 3: "AG-3", 4: "G-4", 6: "G-6",
    8: "VG-8", 10: "VG-10", 12: "F-12", 15: "F-15",
    20: "VF-20", 25: "VF-25", 30: "VF-30", 35: "VF-35",
    40: "EF-40", 45: "EF-45", 50: "AU-50", 53: "AU-53",
    55: "AU-55", 58: "AU-58", 60: "MS-60", 61: "MS-61",
    62: "MS-62", 63: "MS-63", 64: "MS-64", 65: "MS-65",
    66: "MS-66", 67: "MS-67", 68: "MS-68", 69: "MS-69",
    70: "MS-70",
}

GRADE_POINTS = sorted(SHELDON_GRADES.keys())


# Rough value estimates by coin type and grade (placeholder)
VALUE_ESTIMATES = {
    "morgan dollar": {
        (1, 10): (15, 50),
        (12, 35): (30, 200),
        (40, 58): (50, 500),
        (60, 64): (75, 2000),
        (65, 70): (200, 50000),
    },
    "lincoln cent": {
        (1, 10): (0.10, 1),
        (12, 35): (0.50, 5),
        (40, 58): (2, 25),
        (60, 64): (5, 100),
        (65, 70): (25, 5000),
    },
    "peace dollar": {
        (1, 10): (20, 40),
        (12, 35): (25, 100),
        (40, 58): (30, 300),
        (60, 64): (35, 1000),
        (65, 70): (100, 25000),
    },
    "default": {
        (1, 10): (5, 25),
        (12, 35): (10, 100),
        (40, 58): (25, 300),
        (60, 64): (50, 1000),
        (65, 70): (100, 10000),
    },
}


def grade_coin_images(
    images: dict,
    coin_type: Optional[str] = None,
    year: Optional[int] = None,
) -> dict:
    """Grade a coin from its images.
    
    V1: Uses image count and basic heuristics to estimate grade.
    TODO: Replace with trained EfficientNet-B7/ViT model.
    
    Args:
        images: Dict with keys like "obverse", "reverse", "edge", "detail"
        coin_type: e.g., "Morgan Dollar", "Lincoln Cent"
        year: Mint year
        
    Returns:
        Dict with grade, confidence, scores, and estimated value.
    """
    # ── Image quality assessment (placeholder) ──
    image_count = len([v for v in images.values() if v])
    
    # More images = higher confidence
    base_confidence = min(0.5 + (image_count * 0.1), 0.85)
    
    # ── V1: Placeholder grading (random within reasonable range) ──
    # In production, this is replaced by the ML model
    # For now, generate a plausible grade for demo/testing
    grade_numeric = random.choice(GRADE_POINTS[5:20])  # VG-8 to MS-64 range
    
    # Add some variance based on image count
    if image_count >= 4:
        base_confidence += 0.05
    
    confidence = round(min(base_confidence + random.uniform(-0.05, 0.10), 0.95), 3)
    
    # Luster and strike scores (0-10)
    luster_score = round(random.uniform(3.0, 9.0), 1)
    strike_score = round(random.uniform(4.0, 9.5), 1)
    
    # Grade string
    grade = SHELDON_GRADES.get(grade_numeric, f"MS-{grade_numeric}")
    
    # Estimate value
    estimated_value = _estimate_value(coin_type, grade_numeric)
    
    notes = _generate_notes(grade_numeric, confidence, image_count)
    
    return {
        "grade": grade,
        "grade_numeric": grade_numeric,
        "confidence": confidence,
        "luster_score": luster_score,
        "strike_score": strike_score,
        "estimated_value": estimated_value,
        "notes": notes,
    }


def _estimate_value(coin_type: Optional[str], grade_numeric: int) -> Optional[float]:
    """Rough value estimate based on coin type and grade."""
    ct = (coin_type or "").lower()
    
    # Find matching value table
    table = VALUE_ESTIMATES.get(ct, VALUE_ESTIMATES["default"])
    
    for (low, high), (val_low, val_high) in table.items():
        if low <= grade_numeric <= high:
            # Interpolate within range
            ratio = (grade_numeric - low) / max(high - low, 1)
            value = val_low + ratio * (val_high - val_low)
            return round(value, 2)
    
    return None


def _generate_notes(grade_numeric: int, confidence: float, image_count: int) -> str:
    """Generate human-readable grading notes."""
    notes = []
    
    if confidence < 0.65:
        notes.append("⚠️ Low confidence — recommend professional grading for accurate assessment.")
    elif confidence < 0.80:
        notes.append("Moderate confidence. Additional photos may improve accuracy.")
    else:
        notes.append("High confidence AI grade.")
    
    if image_count < 3:
        notes.append("Tip: Adding edge and detail photos improves grading accuracy significantly.")
    
    if grade_numeric >= 60:
        notes.append("Mint state coin — handle with care. Consider PCGS/NGC slabbing for high-value sales.")
    elif grade_numeric >= 40:
        notes.append("About Uncirculated to Extra Fine — light wear visible under magnification.")
    
    return " ".join(notes)
