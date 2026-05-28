"""Billing routes — Stripe Connect onboarding, subscriptions, webhooks."""

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
    create_subscription_checkout,
)

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


# ──────────────────── Subscriptions (Buyers) ────────────────────

@router.post("/subscribe/{tier}")
def subscribe(
    tier: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Start a subscription checkout for Pro or Dealer tier."""
    if tier not in ("pro", "dealer"):
        raise HTTPException(status_code=400, detail="Tier must be 'pro' or 'dealer'")

    # Create Stripe customer if needed
    if not user.stripe_customer_id:
        customer = stripe.Customer.create(
            email=user.email,
            name=user.name,
            metadata={"user_id": user.id, "platform": "coinmatch"},
        )
        user.stripe_customer_id = customer.id
        db.commit()

    url = create_subscription_checkout(
        customer_id=user.stripe_customer_id,
        tier=tier,
        success_url=f"{settings.APP_URL}/dashboard?subscription=success",
        cancel_url=f"{settings.APP_URL}/pricing?subscription=cancelled",
    )
    return {"checkout_url": url}


# ──────────────────── Webhook ────────────────────

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
