"""Whop integration — subscription billing for Pro Collector & Dealer tiers.

Whop replaces Stripe Checkout for these subscription tiers. The peer-to-peer
coin sales between buyers and sellers still go through Stripe Connect (see
app/services/stripe_connect.py) — Whop only handles subscription products.

Webhook signature verification follows the Standard Webhooks spec:
  HMAC-SHA256 of "{webhook-id}.{webhook-timestamp}.{body}" using the base64-decoded
  secret, output base64-encoded. Signature header value is "v1,<base64-sig>".
"""

import base64
import hashlib
import hmac
import time
from typing import Optional

from app.config import settings


# Whop's webhook timestamps must be within this window of the current time
# (replay protection). 5 minutes matches Whop's published default.
MAX_TIMESTAMP_SKEW_SECONDS = 300


def verify_signature(
    webhook_id: str,
    webhook_timestamp: str,
    webhook_signature: str,
    body: bytes,
    secret: Optional[str] = None,
) -> bool:
    """Verify a Whop webhook signature.

    Args:
        webhook_id: value of the `webhook-id` header
        webhook_timestamp: value of the `webhook-timestamp` header (unix seconds)
        webhook_signature: value of the `webhook-signature` header (e.g. "v1,<b64>")
        body: raw request body bytes (do NOT use parsed JSON)
        secret: webhook secret from Whop dashboard; defaults to settings.WHOP_WEBHOOK_SECRET

    Returns:
        True iff the signature matches and the timestamp is within the skew window.
    """
    secret = secret or settings.WHOP_WEBHOOK_SECRET
    if not secret:
        return False
    if not webhook_id or not webhook_timestamp or not webhook_signature:
        return False

    try:
        ts_int = int(webhook_timestamp)
    except (TypeError, ValueError):
        return False
    if abs(time.time() - ts_int) > MAX_TIMESTAMP_SKEW_SECONDS:
        return False

    try:
        secret_bytes = base64.b64decode(secret)
    except (ValueError, TypeError):
        return False

    signed_payload = f"{webhook_id}.{webhook_timestamp}.".encode() + body
    expected_b64 = base64.b64encode(
        hmac.new(secret_bytes, signed_payload, hashlib.sha256).digest()
    ).decode()

    for part in webhook_signature.split(" "):
        version, _, sig = part.partition(",")
        if version == "v1" and hmac.compare_digest(sig, expected_b64):
            return True
    return False


def tier_from_event(event: dict) -> Optional[str]:
    """Pull the CoinMatch tier name out of a Whop membership event payload.

    We tag each Whop product with metadata.tier ("pro" or "dealer") so the
    webhook can route the event to the correct CoinMatch SubscriptionTier.
    Falls back to inspecting the plan/product slug if metadata is missing.
    """
    data = event.get("data") or {}
    metadata = data.get("metadata") or {}
    tier = metadata.get("tier")
    if tier in ("pro", "dealer"):
        return tier

    slug = (data.get("plan", {}) or {}).get("plan_type") or data.get("plan_id") or ""
    slug = str(slug).lower()
    if "dealer" in slug:
        return "dealer"
    if "pro" in slug:
        return "pro"
    return None


def coinmatch_user_id_from_event(event: dict) -> Optional[str]:
    """Pull the CoinMatch user id we stamped into checkout metadata."""
    data = event.get("data") or {}
    metadata = data.get("metadata") or {}
    return metadata.get("coinmatch_user_id") or metadata.get("user_id")


def whop_user_id_from_event(event: dict) -> Optional[str]:
    """Whop's user id for the customer (their account on Whop, not ours)."""
    data = event.get("data") or {}
    return data.get("user_id") or data.get("user", {}).get("id")


def whop_membership_id_from_event(event: dict) -> Optional[str]:
    data = event.get("data") or {}
    return data.get("id") if event.get("type", "").startswith("membership.") else data.get("membership_id")
