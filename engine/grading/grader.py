"""AI Coin Grading Engine — Claude Opus 4.7 Multimodal Vision.

Sends the seller's uploaded photos (obverse, reverse, optional edge + detail)
to Anthropic's Claude with a structured prompt focused on the Sheldon scale,
luster, strike quality, and surface wear. Falls back to a heuristic grader
when ANTHROPIC_API_KEY is unset (useful for local dev + investor demos).

Returns a CoinMatch-shaped dict: grade, grade_numeric, confidence, luster_score,
strike_score, estimated_value, notes, ai_metadata.
"""

import os
import re
import json
import base64
import logging
import random
import mimetypes
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


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

# Rough value bands (USD) by coin type and Sheldon grade range.
VALUE_ESTIMATES = {
    "morgan dollar": {
        (1, 10): (15, 50), (12, 35): (30, 200), (40, 58): (50, 500),
        (60, 64): (75, 2000), (65, 70): (200, 50000),
    },
    "lincoln cent": {
        (1, 10): (0.10, 1), (12, 35): (0.50, 5), (40, 58): (2, 25),
        (60, 64): (5, 100), (65, 70): (25, 5000),
    },
    "peace dollar": {
        (1, 10): (20, 40), (12, 35): (25, 100), (40, 58): (30, 300),
        (60, 64): (35, 1000), (65, 70): (100, 25000),
    },
    "default": {
        (1, 10): (5, 25), (12, 35): (10, 100), (40, 58): (25, 300),
        (60, 64): (50, 1000), (65, 70): (100, 10000),
    },
}

CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-opus-4-7")
UPLOAD_ROOT = Path(os.getenv("UPLOAD_DIR", "static/uploads")).resolve()


def grade_coin_images(
    images: dict,
    coin_type: Optional[str] = None,
    year: Optional[int] = None,
) -> dict:
    """Grade a coin from its uploaded images using Claude Vision.

    Args:
        images: Dict like {"obverse": "/static/uploads/{id}/obverse.jpg", ...}
        coin_type: e.g., "Morgan Dollar", "Lincoln Cent"
        year: Mint year (e.g., 1921)

    Returns:
        Standard CoinMatch grade payload.
    """
    image_paths = {label: path for label, path in images.items() if path}
    if len(image_paths) < 2:
        return {
            "error": "Minimum 2 photos (obverse + reverse) required for grading.",
            "confidence": 0.0,
            "grade": "N/A",
            "grade_numeric": 0,
            "luster_score": 0.0,
            "strike_score": 0.0,
            "estimated_value": None,
            "notes": "Upload at least obverse and reverse images.",
            "ai_metadata": {"model": "none", "image_count": len(image_paths)},
        }

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key:
        try:
            return _grade_with_claude(image_paths, coin_type, year, api_key)
        except Exception as e:
            logger.exception("Claude grading failed, falling back to heuristic: %s", e)

    return _heuristic_grade(image_paths, coin_type)


# ──────────────────── Claude Vision grader ────────────────────

_GRADING_PROMPT = """You are a senior numismatic grader for CoinMatch, evaluating
a coin against the Sheldon 1-70 grading scale used by PCGS and NGC.

The seller has uploaded {n} photo(s): {labels}.
Coin type (claimed by seller): {coin_type}
Year (claimed by seller): {year}

Examine the images for:
- **Surface wear**: high-point wear, friction, scratches, contact marks
- **Luster**: mint frost, cartwheel effect, prooflike fields (mint state coins)
- **Strike quality**: detail sharpness on devices (Liberty's hair, eagle feathers, leaves, stars)
- **Eye appeal**: toning, color, patina, originality
- **Damage**: cleaning, polishing, environmental damage, rim dings

Return a JSON object with EXACTLY these keys and nothing else:
{{
  "grade_numeric": <integer from this set: 1,2,3,4,6,8,10,12,15,20,25,30,35,40,45,50,53,55,58,60,61,62,63,64,65,66,67,68,69,70>,
  "confidence": <float 0.0-1.0 reflecting your certainty given photo quality and detail visible>,
  "luster_score": <float 0.0-10.0; 10 = full booming luster, 0 = no luster>,
  "strike_score": <float 0.0-10.0; 10 = razor-sharp strike, 0 = mushy/weak>,
  "notes": "<2-3 sentence professional summary of grade rationale, what you can/cannot see, and any flags like cleaning, damage, or counterfeit indicators. Be honest. If you cannot see enough detail, lower the confidence and say so.>"
}}

Output ONLY the JSON object. No prose, no markdown fences, no preamble.
If image quality is too poor to grade reliably, set confidence below 0.5 and explain in notes."""


def _grade_with_claude(
    image_paths: dict,
    coin_type: Optional[str],
    year: Optional[int],
    api_key: str,
) -> dict:
    """Call Claude Opus 4.7 with the coin images and parse the structured grade."""
    from anthropic import Anthropic

    client = Anthropic(api_key=api_key)

    content = []
    for label, web_path in image_paths.items():
        data, media_type = _load_image_b64(web_path)
        if not data:
            continue
        content.append({"type": "text", "text": f"[{label.upper()}]"})
        content.append({
            "type": "image",
            "source": {"type": "base64", "media_type": media_type, "data": data},
        })

    if not content:
        raise RuntimeError("No readable image files on disk")

    prompt = _GRADING_PROMPT.format(
        n=len(image_paths),
        labels=", ".join(image_paths.keys()),
        coin_type=coin_type or "unknown",
        year=year or "unknown",
    )
    content.append({"type": "text", "text": prompt})

    resp = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": content}],
    )

    text = "".join(b.text for b in resp.content if getattr(b, "type", None) == "text").strip()
    parsed = _extract_json(text)

    grade_numeric = int(parsed["grade_numeric"])
    if grade_numeric not in SHELDON_GRADES:
        grade_numeric = min(GRADE_POINTS, key=lambda g: abs(g - grade_numeric))
    confidence = float(parsed["confidence"])
    luster = float(parsed.get("luster_score", 0))
    strike = float(parsed.get("strike_score", 0))
    notes = str(parsed.get("notes", "")).strip()

    grade_label = SHELDON_GRADES[grade_numeric] if confidence >= 0.5 else "UNCERTAIN"
    estimated_value = _estimate_value(coin_type, grade_numeric) if grade_label != "UNCERTAIN" else None

    return {
        "grade": grade_label,
        "grade_numeric": grade_numeric,
        "confidence": round(confidence, 3),
        "luster_score": round(luster, 1),
        "strike_score": round(strike, 1),
        "estimated_value": estimated_value,
        "notes": notes,
        "ai_metadata": {
            "model": CLAUDE_MODEL,
            "analyzed_at": datetime.utcnow().isoformat(),
            "image_count": len(image_paths),
            "tokens": {
                "input": resp.usage.input_tokens,
                "output": resp.usage.output_tokens,
            },
        },
    }


def _load_image_b64(web_path: str) -> tuple[Optional[str], str]:
    """Resolve a web path like /static/uploads/{id}/obverse.jpg to disk and base64 it."""
    rel = web_path.lstrip("/")
    if rel.startswith("static/uploads/"):
        rel = rel[len("static/uploads/"):]
    candidate = UPLOAD_ROOT / rel
    if not candidate.exists():
        logger.warning("Image file not found: %s (resolved to %s)", web_path, candidate)
        return None, "image/jpeg"
    media_type, _ = mimetypes.guess_type(candidate.name)
    if media_type not in ("image/jpeg", "image/png", "image/webp", "image/gif"):
        media_type = "image/jpeg"
    with open(candidate, "rb") as f:
        return base64.standard_b64encode(f.read()).decode("ascii"), media_type


def _extract_json(text: str) -> dict:
    """Pull the first JSON object out of Claude's response text."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON object found in model response: {text[:200]}")
    return json.loads(match.group(0))


# ──────────────────── Heuristic fallback (demo / no API key) ────────────────────

def _heuristic_grade(image_paths: dict, coin_type: Optional[str]) -> dict:
    """Local fallback when ANTHROPIC_API_KEY is unset — used for demos."""
    has_edge = "edge" in image_paths
    has_detail = "detail" in image_paths
    image_count = len(image_paths)

    grade_numeric = random.choice([63, 64, 65, 66, 67]) if has_detail else random.choice(GRADE_POINTS[10:25])
    luster_score = round(random.uniform(5.0, 9.5) if image_count >= 3 else random.uniform(3.0, 7.0), 1)
    strike_score = round(random.uniform(6.0, 9.8) if has_detail else random.uniform(4.0, 7.0), 1)

    base_confidence = 0.60
    if image_count >= 3: base_confidence += 0.15
    if has_edge: base_confidence += 0.05
    if has_detail: base_confidence += 0.10
    confidence = round(min(base_confidence, 0.98), 3)

    grade = SHELDON_GRADES.get(grade_numeric, f"MS-{grade_numeric}") if confidence >= 0.65 else "UNCERTAIN"
    estimated_value = _estimate_value(coin_type, grade_numeric) if grade != "UNCERTAIN" else None

    return {
        "grade": grade,
        "grade_numeric": grade_numeric,
        "confidence": confidence,
        "luster_score": luster_score,
        "strike_score": strike_score,
        "estimated_value": estimated_value,
        "notes": "Heuristic grade — set ANTHROPIC_API_KEY for real Claude Vision analysis.",
        "ai_metadata": {
            "model": "heuristic-fallback",
            "analyzed_at": datetime.utcnow().isoformat(),
            "image_count": image_count,
            "has_edge": has_edge,
            "has_detail": has_detail,
        },
    }


def _estimate_value(coin_type: Optional[str], grade_numeric: int) -> Optional[float]:
    ct = (coin_type or "").lower()
    table = VALUE_ESTIMATES.get(ct, VALUE_ESTIMATES["default"])
    for (low, high), (val_low, val_high) in table.items():
        if low <= grade_numeric <= high:
            ratio = (grade_numeric - low) / max(high - low, 1)
            return round(val_low + ratio * (val_high - val_low), 2)
    return None
