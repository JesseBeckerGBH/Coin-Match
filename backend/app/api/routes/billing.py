"""Billing routes — Stripe Connect (marketplace) + Whop (subscriptions) + webhooks.

Stripe Connect: peer-to-peer coin sales between buyers and sellers. Funds flow
buyer → platform → seller via Express connected accounts. Required.

Whop: Pro Collector ($19/mo) and Dealer ($99/mo) subscriptions. Replaces what
used to be Stripe Checkout subscriptions.
"""

import json
import logging

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User, SubscriptionTier
from app.models.transaction import Transaction, TransactionStatus
from app.models.coin import Coin, CoinStatus
from app.services.auth import get_current_user
from app.services.stripe_connect import (
    create_connect_account,
    create_onboarding_link,
)
from app.services import whop

log = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY
router = APIRouter(prefix="/api/billing", tags=["billing"])


# ──────────────────── Stripe Connect (Sellers) ────────────────────

@router.post("/connect/onboard")
def seller_onboard(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Start Stripe Connect onboarding for a seller."""
    if user.stripe_connect_account_id:
        # Already has an account — generate a new onboarding link (in case they didn't finish)
        url = create_onboarding_link(
            user.stripe_connect_account_id,
            return_url=f"{settings.APP_URL}/dashboard/seller?stripe=success",
            refresh_url=f"{settings.APP_URL}/dashboard/seller?stripe=refresh",
        )
        return {"url": url, "status": "existing_account"}

    result = create_connect_account(user.email, user.user_type.value)
    user.stripe_connect_account_id = result["account_id"]
    db.commit()

    url = create_onboarding_link(
        result["account_id"],
        return_url=f"{settings.APP_URL}/dashboard/seller?stripe=success",
        refresh_url=f"{settings.APP_URL}/dashboard/seller?stripe=refresh",
    )
    return {"url": url, "status": "new_account"}


@router.get("/connect/status")
def connect_status(user: User = Depends(get_current_user)):
    """Check if seller's Stripe Connect account is active."""
    if not user.stripe_connect_account_id:
        return {"connected": False, "charges_enabled": False}

    account = stripe.Account.retrieve(user.stripe_connect_account_id)
    return {
        "connected": True,
        "charges_enabled": account.charges_enabled,
        "payouts_enabled": account.payouts_enabled,
        "details_submitted": account.details_submitted,
    }


# ──────────────────── Subscriptions (Buyers) — via Whop ────────────────────

@router.post("/subscribe/{tier}")
def subscribe(
    tier: str,
    user: User = Depends(get_current_user),
):
    """Return the Whop checkout URL for the requested tier.

    The frontend redirects the user to this URL. Whop handles payment, account
    creation, recurring billing, and the customer portal. On success Whop fires
    a webhook to /api/billing/whop-webhook which flips user.tier here.

    We append metadata so the webhook can map the Whop membership back to the
    CoinMatch user record.
    """
    if tier not in ("pro", "dealer"):
        raise HTTPException(status_code=400, detail="Tier must be 'pro' or 'dealer'")

    base_url = (
        settings.WHOP_PRO_CHECKOUT_URL if tier == "pro"
        else settings.WHOP_DEALER_CHECKOUT_URL
    )
    if not base_url:
        raise HTTPException(
            status_code=503,
            detail=f"Whop {tier} checkout URL is not configured. Set WHOP_{tier.upper()}_CHECKOUT_URL.",
        )

    sep = "&" if "?" in base_url else "?"
    checkout_url = (
        f"{base_url}{sep}"
        f"metadata[coinmatch_user_id]={user.id}"
        f"&metadata[tier]={tier}"
        f"&email={user.email}"
    )
    return {"checkout_url": checkout_url, "provider": "whop"}


# ──────────────────── Whop Webhook ────────────────────

@router.post("/whop-webhook")
async def whop_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Whop subscription events: activated, deactivated.

    On membership.activated: flip user.tier to pro/dealer based on metadata.
    On membership.deactivated: drop user back to free.
    """
    body = await request.body()
    webhook_id = request.headers.get("webhook-id", "")
    webhook_timestamp = request.headers.get("webhook-timestamp", "")
    webhook_signature = request.headers.get("webhook-signature", "")

    if not whop.verify_signature(webhook_id, webhook_timestamp, webhook_signature, body):
        raise HTTPException(status_code=401, detail="Invalid Whop webhook signature")

    try:
        event = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Malformed JSON body")

    event_type = event.get("type", "")
    log.info("Whop webhook received: id=%s type=%s", webhook_id, event_type)

    if event_type == "membership.activated":
        tier = whop.tier_from_event(event)
        coinmatch_user_id = whop.coinmatch_user_id_from_event(event)
        whop_user_id = whop.whop_user_id_from_event(event)
        whop_membership_id = whop.whop_membership_id_from_event(event)

        user = None
        if coinmatch_user_id:
            user = db.query(User).filter(User.id == coinmatch_user_id).first()
        if not user and whop_user_id:
            user = db.query(User).filter(User.whop_user_id == whop_user_id).first()
        if not user:
            log.warning("Whop membership.activated for unknown user: %s", event.get("data", {}))
            return {"received": True, "matched_user": False}

        if tier == "dealer":
            user.tier = SubscriptionTier.DEALER
        elif tier == "pro":
            user.tier = SubscriptionTier.PRO
        if whop_user_id:
            user.whop_user_id = whop_user_id
        if whop_membership_id:
            user.whop_membership_id = whop_membership_id
        db.commit()
        return {"received": True, "matched_user": True, "tier": user.tier.value}

    if event_type == "membership.deactivated":
        whop_membership_id = whop.whop_membership_id_from_event(event)
        whop_user_id = whop.whop_user_id_from_event(event)
        user = None
        if whop_membership_id:
            user = db.query(User).filter(User.whop_membership_id == whop_membership_id).first()
        if not user and whop_user_id:
            user = db.query(User).filter(User.whop_user_id == whop_user_id).first()
        if user:
            user.tier = SubscriptionTier.FREE
            user.whop_membership_id = None
            db.commit()
            return {"received": True, "matched_user": True, "tier": user.tier.value}
        return {"received": True, "matched_user": False}

    # Other events (payment.succeeded, refund.created, etc.) — acknowledge but no-op for now.
    return {"received": True, "event_type": event_type, "action": "ignored"}


# ──────────────────── Stripe Webhook (Connect / coin-sale events only) ────────────────────

@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Stripe webhooks for payments, subscriptions, and Connect."""
    payload = await request.body()
    sig = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig, settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    event_type = event["type"]
    data = event["data"]["object"]

    # ── Payment succeeded (coin purchase) ──
    if event_type == "payment_intent.succeeded":
        pi_id = data["id"]
        txn = db.query(Transaction).filter(
            Transaction.stripe_payment_intent_id == pi_id
        ).first()
        if txn:
            txn.status = TransactionStatus.PAYMENT_RECEIVED
            db.commit()

    # ── Subscription events ──
    elif event_type == "customer.subscription.created":
        _handle_subscription(db, data, active=True)

    elif event_type == "customer.subscription.updated":
        _handle_subscription(db, data, active=data.get("status") == "active")

    elif event_type == "customer.subscription.deleted":
        _handle_subscription(db, data, active=False)

    elif event_type == "invoice.payment_failed":
        customer_id = data.get("customer")
        user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
        if user:
            # TODO: Send payment failure notification
            pass

    return {"received": True}


def _handle_subscription(db: Session, data: dict, active: bool):
    """Update user tier based on subscription status."""
    customer_id = data.get("customer")
    user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
    if not user:
        return

    if active:
        # Determine tier from metadata or price
        tier = data.get("metadata", {}).get("tier", "pro")
        user.tier = SubscriptionTier.PRO if tier == "pro" else SubscriptionTier.DEALER
        user.stripe_subscription_id = data.get("id")
    else:
        user.tier = SubscriptionTier.FREE
        user.stripe_subscription_id = None

    db.commit()
